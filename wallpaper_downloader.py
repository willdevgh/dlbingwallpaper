#! python 3
# --*-- encoding: UTF-8 --*--

import logging
from typing import List, Dict
from logging.handlers import RotatingFileHandler
import json


# 3rd-party
import requests


from utils.database import ImageInfo


rotating_file_handler = RotatingFileHandler(f'{__file__[:-3]}.log',
                                            maxBytes=1024 * 1024 * 4, backupCount=3, encoding='utf-8')
rotating_file_handler.setFormatter(logging.Formatter('%(asctime)s[%(levelname)s]%(filename)s(%(lineno)d): %(message)s'))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(rotating_file_handler)

IMAGES = 'images'
STARTDATE, FULLSTARTDATE, ENDDATE, URL, COPYRIGHT = 'startdate', 'fullstartdate', 'enddate', 'url', 'copyright'


class WallpaperDownloader(object):
    def __init__(self):
        self._host = "http://www.bing.com/"  # readonly

    @property
    def host(self):
        return self._host

    def image_archive_url(self, start_date_index=0, day_count=8) -> str:
        """
        用于组装获取 HPImageArchive 的 URL
        :param start_date_index: 表示请求的日期索引(倒序): 0: 今天; 1: 昨天; 2: 前天 ......
        :param day_count: 表示请求的天数: 1: 今天; 2: 昨天，今天; 3: 前天，昨天，今天 ......
        :return: url
        """
        url = f"{self._host}/HPImageArchive.aspx?format=js&idx={start_date_index}&n={day_count}"
        return url

    def image_archive_dict(self, start_date_index=0, day_count=8) -> Dict[str, str]:
        """
        获取带有图片下载 url 的字典
        :param start_date_index:
        :param day_count:
        :return:
        """
        res = requests.get(self.image_archive_url(start_date_index, day_count))
        d = json.loads(s=res.content.decode())  #, encoding='utf-8')
        return d

    def image_info_list(self, start_date_index=0, day_count=8) -> List[ImageInfo]:
        """

        :param start_date_index:
        :param day_count:
        :return:
        """
        archive: dict = self.image_archive_dict(start_date_index, day_count)
        info_lst = []
        try:
            images_info = archive[IMAGES]
            for _info in images_info:
                info_lst.append(ImageInfo(_info[STARTDATE], _info[FULLSTARTDATE], _info[ENDDATE],
                                          f"{self._host}{_info[URL]}", _info[COPYRIGHT]))
        except KeyError:
            raise KeyError(f'keys: {IMAGES}, {STARTDATE}, {FULLSTARTDATE}, {ENDDATE}, {URL}, {COPYRIGHT}')

        return info_lst

    @staticmethod
    def download_image(image_url: str, save_file_name: str):
        """
        下载图片
        :param image_url:
        :param save_file_name:
        """
        image_data = requests.get(image_url, stream=True)
        with open(save_file_name, 'wb') as image_file:
            for chunk in image_data.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    image_file.write(chunk)
                    image_file.flush()
