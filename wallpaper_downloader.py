#! python 3
# --*-- encoding: UTF-8 --*--

import logging
from logging.handlers import RotatingFileHandler
import xml.etree.ElementTree as ET
import json
from collections import namedtuple

# 3rd-party
import requests

rotating_file_handler = RotatingFileHandler(f'{__file__[:-3]}.log',
                                            maxBytes=1024 * 1024 * 4, backupCount=3, encoding='utf-8')
rotating_file_handler.setFormatter(logging.Formatter('%(asctime)s[%(levelname)s]%(filename)s(%(lineno)d): %(message)s'))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(rotating_file_handler)

IMAGES = 'images'
STARTDATE, FULLSTARTDATE, ENDDATE, URL, COPYRIGHT, TITLE = 'startdate', 'fullstartdate', 'enddate', 'url', 'copyright', 'title'
ImageInfo = namedtuple('ImageInfo', [STARTDATE, FULLSTARTDATE, ENDDATE, URL, COPYRIGHT, TITLE])


class WallpaperDownloader(object):
    def __init__(self):
        self.__host = "http://www.bing.com"  # readonly
        pass

    @property
    def host(self):
        return self.__host

    def image_archive_url(self, start_date_index=0, day_count=8) -> str:
        """
        获取 HPImageArchive 的 URL
        :param start_date_index: 表示请求的日期索引(倒序): 0: 今天; 1: 昨天 ......
        :param day_count: 表示请求的天数: 1: 今天当天; 2: 昨天和今天 ......
        :return: url
        """
        url = f"{self.__host}/HPImageArchive.aspx?format=js&idx={start_date_index}&n={day_count}"
        return url

    def image_archive_dict(self, start_date_index=0, day_count=8) -> bytes:
        """

        :param start_date_index:
        :param day_count:
        :return:
        """
        res = requests.get(self.image_archive_url(start_date_index, day_count))
        d = json.loads(s=res.content.decode())
        return d

    def image_info_list(self, start_date_index=0, day_count=8) -> list:
        archive = self.image_archive_dict(start_date_index, day_count)
        info_list = []
        try:
            images_info = archive[IMAGES]
            for info in images_info:
                info_list.append(ImageInfo(info[STARTDATE], info[FULLSTARTDATE], info[ENDDATE],
                                           f"{self.__host}{info[URL]}", info[COPYRIGHT], info[TITLE]))
        except KeyError:
            raise KeyError(f'keys: {IMAGES}, {STARTDATE}, {FULLSTARTDATE}, {ENDDATE}, {URL}, {COPYRIGHT}, {TITLE}')

        return info_list

    @staticmethod
    def download_image(image_url: str, save_file_name: str):
        """
        下载图片
        :param image_url:
        :param save_file_name:
        :return:
        """
        image_data = requests.get(image_url, stream=True)
        with open(save_file_name, 'wb') as image_file:
            for chunk in image_data.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    image_file.write(chunk)
                    image_file.flush()


if __name__ == "__main__":
    # test
    downloader = WallpaperDownloader()
    info_list: list = downloader.image_info_list(day_count=8)
    print(info_list)
    for i, info in enumerate(info_list):
        print(f"downloading: {info.copyright}")
        downloader.download_image(info.url, f'{info.title}.jpg')
