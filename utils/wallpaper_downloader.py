#! python 3
# --*-- encoding: UTF-8 --*--


import json
import logging
from pathlib import Path

# import xml.etree.ElementTree as ET

from .database import (
    ImageInfo,
    FULLSTARTDATE,
    ENDDATE,
    URL,
    COPYRIGHT,
    COPYRIGHTLINK,
    TITLE,
)

# 3rd-party
import requests

IMAGES = 'images'

logger = logging.getLogger(__name__)


class ImageInfoDownloader:
    """壁纸信息下载类"""

    def __init__(self):
        self.__host = "http://www.bing.com"  # readonly

    @property
    def host(self) -> str:
        return self.__host

    def image_info_list(self, start_date_index: int = 0, day_count: int = 8) -> list[ImageInfo]:
        """获取指定的 ImageInfo 列表

        Args:
            start_date_index (int, optional): 表示请求的日期索引(倒序): 0: 今天; 1: 昨天 ......。 Defaults to 0.
            day_count (int, optional): 表示请求的天数: 1: 今天当天; 2: 昨天和今天 ......。 Defaults to 8.

        Raises:
            KeyError: KeyError

        Returns:
            list[ImageInfo]: ImageInfo 列表
        """
        archive = self.__image_archive_dict(start_date_index, day_count)
        info_list = []
        images_info = archive[IMAGES]
        for info in images_info:
            logger.debug(info)
            info_list.append(
                ImageInfo(
                    info[FULLSTARTDATE],
                    info[ENDDATE],
                    f"{self.__host}{info[URL]}",
                    info[COPYRIGHT],
                    info[COPYRIGHTLINK],
                    info[TITLE],
                )
            )

        return info_list

    def __image_archive_dict(self, start_date_index: int = 0, day_count: int = 8) -> dict:
        """
        获取图片存档字典(private)
        Args:
            start_date_index (int, optional): 表示请求的日期索引(倒序): 0: 今天; 1: 昨天 ......。 Defaults to 0.
            day_count (int, optional): 表示请求的天数: 1: 今天当天; 2: 昨天和今天 ......。 Defaults to 8.

        Returns:
            dict: 图片存档字典
        """
        url = f"{self.__host}/HPImageArchive.aspx?format=js&idx={start_date_index}&n={day_count}"
        res = requests.get(url)
        d = json.loads(s=res.content.decode())
        return d


def download_image(image_url: str, save_file_name: Path | str):
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
