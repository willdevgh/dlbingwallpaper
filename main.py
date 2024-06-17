import os
import base64
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler

from wallpaper_downloader import WallpaperDownloader
from utils.database import WallpaperDatabase, ImageInfo, FULLSTARTDATE, ENDDATE, URL, COPYRIGHT, COPYRIGHTLINK, TITLE
from utils.email import send_email

rotating_file_handler = RotatingFileHandler(f"{__file__[:-3]}.log",
                                            maxBytes=1024 * 1024 * 4, backupCount=3, encoding='utf-8')
rotating_file_handler.setFormatter(logging.Formatter('%(asctime)s[%(levelname)s]%(filename)s(%(lineno)d): %(message)s'))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(rotating_file_handler)

downloader = WallpaperDownloader()
database = WallpaperDatabase(os.path.abspath(os.curdir))

info_list: list = downloader.image_info_list(day_count=8)
logger.debug(info_list)

SMTP_PORT = 25 #587

with database.open_db_context():
    # 下载 & 保存
    for i, info in enumerate(info_list):
        logger.info(f"downloading: {info.copyright}")
        downloader.download_image(info.url, f"{info.enddate}_{info.title}.jpg")
        image_file = Path(os.curdir) / f"{info.enddate}_{info.title}.jpg"
        
        #with open(image_file.absolute(), 'rb') as f:
        data = image_file.read_bytes()
        b64_data = base64.b64encode(data)
        if database.save_info(info, b64_data):
            # todo: send_email('smtp.163.com', SMTP_PORT, 'from mailbox', 'auth_password', ('to mailbox', ), f"[Bing今日美图] {info.title}", (image_file, ))
            pass

        image_file.unlink(missing_ok=True)
    
    # 读取
    '''
    content = database.get_content_by_enddate('20240614', 'data')
    image_data = base64.b64decode(content)
    image_file = Path(os.curdir) / 'image_saved.jpg'
    image_file.write_bytes(image_data)
    '''
    info, image_data = database.get_record_by_enddate('20240613')
    print(info.fullstartdate)
    print(info.enddate)
    print(info.url)
    print(info.copyright)
    print(info.copyrightlink)
    print(info.title)
    image_data = base64.b64decode(image_data)
    image_file = Path(os.curdir) / "20240613.jpg"
    image_file.write_bytes(image_data)
