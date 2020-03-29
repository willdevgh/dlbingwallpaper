#! python 3
# --*-- encoding: UTF-8 --*--

"""
Download wallpapers from cn.bing.com
下载必应壁纸到指定路径下
"""

import sys
import os
import os.path as op
import asyncio
import xml.etree.ElementTree as ET
import logging
from logging.handlers import RotatingFileHandler

import aiohttp
import redo

from utils import WallpaperDatabase
from utils import Spin

rotating_file_handler = RotatingFileHandler(f'{__file__[:-3]}.log',
                                            maxBytes=1024 * 1024 * 4, backupCount=3, encoding='utf-8')
rotating_file_handler.setFormatter(logging.Formatter('%(asctime)s[%(levelname)s]%(filename)s(%(lineno)d): %(message)s'))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(rotating_file_handler)


class DlXmlException(Exception):
    def __init__(self, status, xml_url):
        self.status = status
        self.xml_url = xml_url


class DlException(Exception):
    def __init__(self, full_image_url, save_file_name):
        self.full_image_url = full_image_url
        self.save_file_name = save_file_name


class DbException(Exception):
    def __init__(self, xml_data):
        self.xml_data = xml_data


async def download_todayimageinfo(idx):
    """下载索引内容xml数据
        idx=7 和 idx=8 获取到的内容是一样的
    """
    xml_url = f'http://az517271.vo.msecnd.net/TodayImageService.svc/HPImageArchive?mkt=zh-cn&idx={idx}'

    # 这两天出现下载失败的情况，所以加了redo模块
    for _ in redo.retrier(sleeptime=1, jitter=0):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(xml_url) as resp:
                    if resp.status == 200:
                        return await resp.read()
                        break
                    else:
                        continue
        except:
            # 忽略异常
            continue


async def download_image(full_image_url, save_file_name):
    async with aiohttp.ClientSession() as session:
        async with session.get(full_image_url) as resp:
            image_data = await resp.read()

    with open(save_file_name, 'wb') as image_file:
        image_file.write(image_data)
        image_file.flush()


async def download_and_save_one(idx, save_path, db):
    """下载并保存一张照片的信息
        idx=7 和 idx=8 获取到的内容是一样的
    """
    xml_data = await download_todayimageinfo(idx)
    logger.debug(f"index[{idx}]:\n{xml_data}\n\n")

    if xml_data is None:
        logger.debug("xml_data is none!!!")
    root = ET.fromstring(xml_data)
    start_date = root[0].text
    end_date = root[2].text
    full_image_url = root[6].text
    copyright = root[7].text

    file_name = start_date + '.jpg'
    save_file_name = op.join(save_path, file_name)

    # save file
    try:
        if not op.exists(save_file_name):
            await download_image(full_image_url, save_file_name)
    except Exception as exc:
        raise DlException(full_image_url, save_file_name) from exc
    else:
        # save record
        try:
            if not db.record_exist(start_date):
                db.save_info(start_date, end_date, full_image_url, copyright)
        except Exception as exc:
            raise DbException(xml_data) from exc


async def downloader(save_path, db):
    spin = Spin('Downloading wallpapers from cn.bing.com ...')
    spin.run()
    todo_list = [download_and_save_one(i, save_path, db) for i in range(8, -1, -1)]
    todo_list_iter = asyncio.as_completed(todo_list)
    try:
        for future in todo_list_iter:
            await future
    except DlXmlException as dlXmlExc: # 该处异常已被忽略
        logger.exception("DlXmlException occurred:")
        logger.exception(f"dlXmlExc.xml_url: [{dlXmlExc.xml_url}]")
    except DlException as dlExc:
        try:
            err_msg = dlExc.__cause__.args[0]
        except IndexError:
            err_msg = dlExc.__cause__.__class__.__name__
        if err_msg:
            msg = (f'*** Error for DlException: {err_msg}\n'
                   f'dlExc.save_file_name: [{dlExc.save_file_name}]\n'
                   f'dlExc.full_image_url: [{dlExc.full_image_url}]')
            logger.exception(msg)
        else:
            logger.exception("DlException occurred!")
    except DbException as dbExc:
        logger.exception("DbException occurred:")
        logger.exception(f"dbExc.xml_data[0:16]: [{dbExc.xml_data[0:16]}]")
        try:
            err_msg = dbExc.__cause__.args[0]
        except IndexError:
            err_msg = dbExc.__cause__.__class__.__name__
        if err_msg:
            msg = (f'*** Error for DbException: {err_msg}\n'
                   f'dbExc.xml_data[0:16]: [{dbExc.xml_data[0:16]}]')
            logger.exception(msg)
        else:
            logger.exception("DbException occurred!")
    finally:
        spin.exit()


def download_one(url, full_name):
    oldloop = asyncio.get_event_loop()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(asyncio.wait([download_image(url, full_name)]))
    loop.close()
    asyncio.set_event_loop(oldloop)


def coro_main(save_path, db):
    try:
        loop = asyncio.get_event_loop()
        coro = downloader(save_path, db)
        loop.run_until_complete(coro)
        loop.close()
    except Exception as exc:
        logger.exception(f"Unexpected error: {repr(exc)}")


def download_wallpapers(image_path, database_path):
    # A SQLite database to save every wallpaper's information.
    db = WallpaperDatabase(database_path)
    # start!!
    with db.open_db_context():
        coro_main(image_path, db)


if __name__ == '__main__':
    if sys.version_info.major != 3:
        input("\nPython3 needed!\nPress ENTER to exit.")
        exit(0)

    print("\n")
    script_path = os.path.split(os.path.realpath(__file__))[0]
    image_path = script_path
    if len(sys.argv) >= 2:
        if os.path.isdir(sys.argv[1]):
            image_path = sys.argv[1]

    download_wallpapers(image_path=image_path, database_path=script_path)

    input("\nPress ENTER to exit.")
