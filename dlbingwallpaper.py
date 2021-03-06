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

import aiohttp
import redo

from utils import WallpaperDatabase
from utils import Spin


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


def printExcFileLine():
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)


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
        print("DlXmlException occurred:")
        print(f"dlXmlExc.xml_url: [{dlXmlExc.xml_url}]")
        printExcFileLine()
    except DlException as dlExc:
        try:
            err_msg = dlExc.__cause__.args[0]
        except IndexError:
            err_msg = dlExc.__cause__.__class__.__name__
        if err_msg:
            msg = (f'*** Error for DlException: {err_msg}\n'
                   f'dlExc.save_file_name: [{dlExc.save_file_name}]\n'
                   f'dlExc.full_image_url: [{dlExc.full_image_url}]')
            print(msg)
        else:
            print("DlException occurred!")
        printExcFileLine()
    except DbException as dbExc:
        print("DbException occurred:")
        print(f"dbExc.xml_data[0:16]: [{dbExc.xml_data[0:16]}]")
        try:
            err_msg = dbExc.__cause__.args[0]
        except IndexError:
            err_msg = dbExc.__cause__.__class__.__name__
        if err_msg:
            msg = (f'*** Error for DbException: {err_msg}\n'
                   f'dbExc.xml_data[0:16]: [{dbExc.xml_data[0:16]}]')
            print(msg)
        else:
            print("DbException occurred!")
        printExcFileLine()
    finally:
        spin.exit()


def coro_main(save_path, db):
    try:
        loop = asyncio.get_event_loop()
        coro = downloader(save_path, db)
        loop.run_until_complete(coro)
        loop.close()
    except Exception as exc:
        print(f"Unexpected error: {repr(exc)}")
        printExcFileLine()


if __name__ == '__main__':
    if sys.version_info.major != 3:
        input("\nPython3 needed!\nPress ENTER to exit.")
        exit(0)

    print("\n")
    script_path = os.path.split(os.path.realpath(__file__))[0]
    save_path = script_path

    if len(sys.argv) >= 2:
        if os.path.isdir(sys.argv[1]):
            save_path = sys.argv[1]

    # A SQLite database to save every wallpaper's information.
    db = WallpaperDatabase(script_path)
    # start!!
    with db.open_db_context():
        coro_main(save_path, db)

    input("\nPress ENTER to exit.")