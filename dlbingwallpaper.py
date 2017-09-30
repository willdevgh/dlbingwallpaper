#! python 3
# --*-- encoding: UTF-8 --*--

'''
Download wallpapers from cn.bing.com
下载必应壁纸到指定路径下
'''

import sys
import xml.etree.ElementTree as ET
import os
import os.path as op
import sqlite3
import contextlib

import requests


class WallpaperDatabase:
    """ 数据库调用接口
    """

    def __init__(self, path, is_auto=True):
        self._auto_commit = is_auto
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
        self._db_cur.execute(f"INSERT INTO info VALUES('{start_date}', '{end_date}', '{full_image_url}', '{copyright}')")

        if self._auto_commit:
            self._db_conn.commit()

    def get_copyright(self, startdate):
        copyright_text = 'not found!'
        sql = f"SELECT copyright FROM info WHERE startdate='{startdate}'"
        self._db_cur.execute(sql)
        r = self._db_cur.fetchall()
        if len(r) > 0:
            copyright_text = r[0][0]

        return copyright_text

    def get_fullImageUrl(self, startdate):
        fullImageUrl_text = 'not found!'
        sql = f"SELECT fullImageUrl FROM info WHERE startdate='{startdate}'"
        self._db_cur.execute(sql)
        r = self._db_cur.fetchall()
        if len(r) > 0:
            fullImageUrl_text = r[0][0]

        return fullImageUrl_text

    def record_exist(self, startdate):
        sql = f"SELECT 1 FROM info WHERE startdate='{startdate}'"
        self._db_cur.execute(sql)
        r = self._db_cur.fetchall()
        return len(r) > 0

    def commit(self):
        self._db_conn.commit()


def download(full_image_url, save_file_name):
    image_data = requests.get(full_image_url, stream=True)

    with open(save_file_name, 'wb') as image_file:
        for chunk in image_data.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                image_file.write(chunk)
                image_file.flush()
        image_file.close()



def download_wallpapers():
    print("\nDownload wallpapers from cn.bing.com\n")

    script_path = os.path.abspath('.')

    save_path = script_path

    if len(sys.argv) >= 2:
        if os.path.isdir(sys.argv[1]):
            save_path = sys.argv[1]

    if not save_path.endswith('\\'):
        save_path += '\\'

    if not script_path.endswith('\\'):
        script_path += '\\'

    # A SQLite database to save every wallpaper's information.
    db = WallpaperDatabase(script_path, is_auto=False)

    dl_failed = {}
    sv_failed = {}

    if not op.exists(save_path):
        os.mkdir(save_path)

    with db.open_db_context():
        for i in range(8, -1, -1):
            print(f"****************************index: {i}")
            # download wallpaper's info
            xml_url = f"http://az517271.vo.msecnd.net/TodayImageService.svc/HPImageArchive?mkt=zh-cn&idx={i}"

            try:
                xml_data = requests.get(xml_url)
                root = ET.fromstring(xml_data.text)
            except requests.exceptions.ConnectionError:
                print("raise ConnectionError while downloading wallpaper's information.")
                dl_failed[i] = xml_url + " $ raise ConnectionError."
                continue

            start_date = root[0].text
            end_date = root[2].text
            full_image_url = root[6].text
            copyright = root[7].text

            print(f"wallpaper url: [{full_image_url}]")
            file_name = start_date + '.jpg'
            save_file_name = op.join(save_path, file_name)

            # save file
            if not op.exists(save_file_name):
                try:
                    download(full_image_url, save_file_name)
                    print(f"Download wallpaper '{os.path.basename(save_file_name)}' success!")
                except requests.exceptions.ConnectionError:
                    print("raise ConnectionError while downloading wallpapers.")
                    dl_failed[i] = full_image_url + " $ raise ConnectionError."
            else:
                print(f"Wallpaper named {file_name} is already exist.")
                print(f"You can find it in path '{save_path}'")
                dl_failed[i] = full_image_url + " $ already exist."

            # save record
            if not db.record_exist(start_date):
                try:
                    db.save_info(start_date, end_date, full_image_url, copyright)
                except sqlite3.IntegrityError:
                    print("raise sqlite3.IntegrityError, duplicate key value violates unique constraint.")
                    sv_failed[i] = full_image_url + " $ raise sqlite3.IntegrityError."
            else:
                print(f"Wallpaper named {file_name}'s Record is already exist.")
                dl_failed[i] = full_image_url + " $ already exist."
        db.commit()

    print("")
    if not len(dl_failed) == 0:
        print("Following wallpapers were downloaded failed:")
        for k in dl_failed:
            print(f"index: {k}, url: {dl_failed[k]}")

        print(f"Download finished! You will find some of them in path '{save_path}'.")
    else:
        print(f"Download finished! You will find all of them in path '{save_path}'.")

    print("")
    if not len(sv_failed) == 0:
        print("Following infos were saved failed:")
        for k in sv_failed:
            print(f"index: {k}, url: {sv_failed[k]}")
    else:
        print("All infos were saved in db!")


if __name__ == '__main__':
    if sys.version_info.major != 3:
        input('\nPython3 needed!\nPress any key to exit.')
        exit(0)

    download_wallpapers()
    input("\nPress any key to exit.")
