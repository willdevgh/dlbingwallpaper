#! python 3
# --*-- encoding: UTF-8 --*--

'''
Download wallpapers from cn.bing.com
下载必应壁纸到指定路径下
'''


import sys
import os
import os.path as op
import sqlite3
import contextlib
import asyncio
import xml.etree.ElementTree as ET

import aiohttp


class WallpaperDatabase:
    """ 数据库调用接口
    """

    def __init__(self, path, auto_commit=True):
        self._auto_commit = auto_commit
        self._path = path
        self._db_conn = None
        self._db_cur = None
        if not os.path.exists(os.path.join(self._path, self.db_name)):
            self.create()

    @property
    def db_name(self):
        return "wallpaper.db"

    def create(self):
        sqlstr = '''CREATE TABLE info (
                startdate    TEXT,
                enddate      TEXT,
                fullImageUrl TEXT UNIQUE
                      PRIMARY KEY,
                copyright    TEXT
                );'''
        db_conn = sqlite3.connect(os.path.join(self._path, self.db_name))
        db_conn.execute(sqlstr)

    def set_auto_commit(self, is_auto=True):
        self._auto_commit = is_auto

    @contextlib.contextmanager
    def open_db_context(self):
        self.open()
        yield
        self.close()

    def open(self):
        self._db_conn = sqlite3.connect(os.path.join(self._path, self.db_name))
        self._db_cur = self._db_conn.cursor()

    def close(self):
        if not self._auto_commit:
            self.commit()
        self._db_conn.close()

    def save_info(self, start_date, end_date, full_image_url, copyright):
        copyright = copyright.replace("'", "''")
        self._db_cur.execute("INSERT INTO info VALUES('%s', '%s', '%s', '%s')" \
                             % (start_date, end_date, full_image_url, copyright))

        if self._auto_commit:
            self._db_conn.commit()

    def get_copyright(self, startdate):
        copyright_text = 'not found!'
        sql = "SELECT copyright FROM info WHERE startdate='{}'".format(startdate)
        self._db_cur.execute(sql)
        r = self._db_cur.fetchall()
        if len(r) > 0:
            copyright_text = r[0][0]

        return copyright_text

    def get_fullImageUrl(self, startdate):
        fullImageUrl_text = 'not found!'
        sql = "SELECT fullImageUrl FROM info WHERE startdate='{}'".format(startdate)
        self._db_cur.execute(sql)
        r = self._db_cur.fetchall()
        if len(r) > 0:
            fullImageUrl_text = r[0][0]

        return fullImageUrl_text

    def record_exist(self, startdate):
        sql = "SELECT 1 FROM info WHERE startdate='{}'".format(startdate)
        self._db_cur.execute(sql)
        r = self._db_cur.fetchall()
        return len(r) > 0

    def commit(self):
        self._db_conn.commit()


async def download(full_image_url, save_file_name):
    #--image_data = requests.get(full_image_url, stream=True)
    #image_data = await aiohttp.request('GET', full_image_url)
    async with aiohttp.ClientSession() as session:
        async with session.get(full_image_url) as resp:
            image_data = await resp.read()

    with open(save_file_name, 'wb') as image_file:
        image_file.write(image_data)
        image_file.flush()


async def download_and_save_one(idx, save_path, db):
    xml_url_fmt = 'http://az517271.vo.msecnd.net/TodayImageService.svc/HPImageArchive?mkt=zh-cn&idx={}'
    xml_url = xml_url_fmt.format(idx)

    async with aiohttp.ClientSession() as session:
        async with session.get(xml_url) as resp:
            xml_data = await resp.read()

    root = ET.fromstring(xml_data)
    start_date = root[0].text
    end_date = root[2].text
    full_image_url = root[6].text
    copyright = root[7].text
    print('%s: %s' % (start_date, copyright))

    file_name = start_date + '.jpg'
    save_file_name = op.join(save_path, file_name)

    # save file
    if not op.exists(save_file_name):
        await download(full_image_url, save_file_name)
        print("Download wallpaper '%s' success!" % os.path.basename(save_file_name))
    else:
        print("Wallpaper named %s is already exist." % file_name)
        print("You can find it in path '%s'" % save_path)
        # dl_failed[i] = full_image_url + " $ already exist."

    # save record
    if not db.record_exist(start_date):
        try:
            db.save_info(start_date, end_date, full_image_url, copyright)
        except sqlite3.IntegrityError:
            print("raise sqlite3.IntegrityError, duplicate key value violates unique constraint.")
            # sv_failed[i] = full_image_url + " $ raise sqlite3.IntegrityError."
    else:
        print("Wallpaper named %s's Record is already exist." % file_name)
        # dl_failed[i] = full_image_url + " $ already exist."
    print('-' * 50)


async def downloader(save_path, db):
    todo_list = [download_and_save_one(i, save_path, db) for i in range(8, -1, -1)]
    todo_list_iter = asyncio.as_completed(todo_list)
    for future in todo_list_iter:
        await future

def coro_main(save_path, db):
    loop = asyncio.get_event_loop()
    coro = downloader(save_path, db)
    loop.run_until_complete(coro)
    loop.close()


if __name__ == '__main__':
    print("\nDownloading wallpapers from cn.bing.com ...\n")
    script_path = os.path.abspath('.')
    save_path = script_path

    if len(sys.argv) >= 2:
        if os.path.isdir(sys.argv[1]):
            save_path = sys.argv[1]

    # A SQLite database to save every wallpaper's information.
    db = WallpaperDatabase(script_path, auto_commit=True)

    with db.open_db_context():
        coro_main(save_path, db)

    input("\nPress any key to exit.")
