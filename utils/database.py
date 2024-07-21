#! python 3
# --*-- encoding: UTF-8 --*--

import os
import logging
import sqlite3
import contextlib
from pathlib import Path
from typing import Generator
from collections import namedtuple

FULLSTARTDATE, ENDDATE, URL, COPYRIGHT, COPYRIGHTLINK, TITLE = (
    'fullstartdate',
    'enddate',
    'url',
    'copyright',
    'copyrightlink',
    'title',
)
ImageInfo = namedtuple('ImageInfo', [FULLSTARTDATE, ENDDATE, URL, COPYRIGHT, COPYRIGHTLINK, TITLE])

logger = logging.getLogger(__name__)


class WallpaperDatabase:
    """数据库调用接口"""

    def __init__(self, path: str | Path, auto_commit=True):
        self.__auto_commit = auto_commit
        self.__filename = "wallpaper.db"
        self.__path = Path(path)
        self.__full_path_file = self.__path / self.__filename
        self.__tbl_image_info = "TblImageInfo"
        self.__db_conn = None
        self.__db_cur = None
        if not os.path.exists(self.__full_path_file):
            logger.info(f"database file(*.db) not exist! create database file in path: {self.__path}")
            self.create()

    @property
    def db_name(self) -> str:
        return self.__filename

    @property
    def table_name_image_info(self) -> str:
        return self.__tbl_image_info

    def create(self) -> None:
        sqlstr = f'''CREATE TABLE IF NOT EXISTS {self.table_name_image_info} (
                fullstartdate   TEXT,
                enddate    TEXT UNIQUE PRIMARY KEY,
                url    TEXT,
                copyright    TEXT,
                copyrightlink    TEXT,
                title    TEXT,
                data    BLOB
                );'''
        logger.debug(sqlstr)
        self.__db_conn = sqlite3.connect(self.__full_path_file)
        self.__db_cur = self.__db_conn.execute(sqlstr)

    def set_auto_commit(self, is_auto=True):
        self.__auto_commit = is_auto

    @contextlib.contextmanager
    def open_db_context(self) -> Generator[None, None, None]:
        self.open()
        yield
        self.close()

    def open(self) -> None:
        if not self.__db_conn:
            self.__db_conn = sqlite3.connect(self.__full_path_file)
            self.__db_cur = self.__db_conn.cursor()

    def close(self) -> None:
        if not self.__db_conn:
            return

        if not self.__auto_commit:
            self.commit()

        self.__db_conn.close()
        self.__db_conn = None

    def save_info(self, info: ImageInfo, data: bytes) -> bool:
        if not self.__db_conn:
            return

        try:
            # self._db_cur.execute(f"INSERT INTO {self.table_name_image_info} VALUES('{fullstartdate}', '{enddate}', '{url}', '{copyright}', '{copyrightlink}', '{title}', {data})")
            sqlstr = f"INSERT INTO {self.table_name_image_info} VALUES(?,?,?,?,?,?,?);"
            logger.debug(sqlstr)
            self.__db_cur.execute(
                sqlstr,
                (
                    info.fullstartdate,
                    info.enddate,
                    info.url,
                    info.copyright.replace("'", "''"),
                    info.copyrightlink,
                    info.title,
                    data,
                ),
            )
            if self.__auto_commit:
                self.__db_conn.commit()

            return True
        except sqlite3.DatabaseError as e:
            logger.error(f"sqlite3.DatabaseError: errorcode: {e.sqlite_errorcode}, errorname: {e.sqlite_errorname}")
            return False

    def get_content_by_enddate(self, enddate: str, field: str) -> None | str | bytes:
        if not self.__db_conn:
            return

        sqlstr = f"SELECT {field} FROM {self.table_name_image_info} WHERE enddate='{enddate}'"
        logger.debug(sqlstr)
        self.__db_cur.execute(sqlstr)
        r = self.__db_cur.fetchone()
        return None if r is None else r[0]

    def get_record_by_enddate(self, enddate: str) -> tuple[ImageInfo, bytes]:
        if not self.__db_conn:
            return

        sqlstr = f"SELECT * FROM {self.table_name_image_info} WHERE enddate='{enddate}'"
        logger.debug(sqlstr)
        self.__db_cur.execute(sqlstr)
        r = self.__db_cur.fetchone()
        info = ImageInfo(*r[:-1])
        return info, r[6]

    def record_exist(self, enddate: str) -> bool:
        if not self.__db_conn:
            return

        sqlstr = f"SELECT 1 FROM {self.table_name_image_info} WHERE enddate='{enddate}'"
        logger.debug(sqlstr)
        self.__db_cur.execute(sqlstr)
        r = self.__db_cur.fetchone()
        return r is not None

    def commit(self) -> None:
        if not self.__db_conn:
            return

        self.__db_conn.commit()
