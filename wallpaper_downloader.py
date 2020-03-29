#! python 3
# --*-- encoding: UTF-8 --*--

import logging
from logging.handlers import RotatingFileHandler
import xml.etree.ElementTree as ET

import requests
from PyQt5.QtCore import QThread, pyqtSignal

from utils import WallpaperDatabase

rotating_file_handler = RotatingFileHandler(f'{__file__[:-3]}.log',
                                            maxBytes=1024 * 1024 * 4, backupCount=3, encoding='utf-8')
rotating_file_handler.setFormatter(logging.Formatter('%(asctime)s[%(levelname)s]%(filename)s(%(lineno)d): %(message)s'))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(rotating_file_handler)


class WallpaperDownloader(object):
    def __init__(self):
        self.__host = "http://www.bing.com"  # readonly
        pass

    @property
    def host(self):
        return self.__host

    def image_archive_url(self, idx=0, n=8) -> str:
        """
        获取 HPImageArchive 的 URL
        :param idx: 表示请求的日期索引(倒序): 0: 今天; 1: 昨天 ......
        :param n: 表示请求的天数: 1: 今天当天; 2: 昨天和今天 ......
        :return: url
        """
        url = f"{self.__host}/HPImageArchive.aspx?format=js&idx={idx}&n={n}"
        return url


if __name__ == "__main__":
    # test
    downloader = WallpaperDownloader()
    print(downloader.host)
    print(downloader.image_archive_url(n=8))
