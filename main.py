import os
import base64
from pathlib import Path
from configparser import ConfigParser
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

CONFIG_FILE = 'config.ini'

def main():
    downloader = WallpaperDownloader()
    database = WallpaperDatabase(os.path.abspath(os.curdir))
    conf = ConfigParser()
    if not conf.read(Path(os.path.abspath(os.curdir)) / CONFIG_FILE):
        print("config.ini not found!")
        return
    
    email_section = conf['email']
    if not email_section:
        print("section 'email' not found in config.ini!")
        return
    
    smtp_host = email_section.get('smtp_host')
    smtp_port = email_section.getint('smtp_port')
    auth_password = email_section.get('auth_password')
    from_mailbox = email_section.get('from')
    to_mailboxes = email_section.get('to').split(',')
    if False in (bool(smtp_host), bool(smtp_port), bool(auth_password), bool(from_mailbox), bool(to_mailboxes)):
        print("parameter missing in config.ini!")
        return

    info_list: list = downloader.image_info_list(day_count=8)
    logger.debug(info_list)

    SMTP_PORT = 25 #587 

    with database.open_db_context():
        # 下载 & 保存
        
        for i, info in enumerate(info_list):
            logger.info(f"downloading: {info.copyright}")
            downloader.download_image(info.url, f"{info.enddate}_{info.title}.jpg")
            image_file = Path(os.curdir) / f"{info.enddate}_{info.title}.jpg"
            data = image_file.read_bytes()
            b64_data = base64.b64encode(data)
            if database.save_info(info, b64_data):
                send_email(smtp_host, smtp_port, from_mailbox, auth_password, to_mailboxes, f"[Bing今日美图] {info.title}", (image_file, ))
                pass

            image_file.unlink(missing_ok=True)
        
        # 读取
        '''
        content = database.get_content_by_enddate('20240614', 'data')
        image_data = base64.b64decode(content)
        image_file = Path(os.curdir) / 'image_saved.jpg'
        image_file.write_bytes(image_data)
        
        info, image_data = database.get_record_by_enddate('20240621')
        print(info.fullstartdate)
        print(info.enddate)
        print(info.url)
        print(info.copyright)
        print(info.copyrightlink)
        print(info.title)
        image_data = base64.b64decode(image_data)
        image_file = Path(os.curdir) / "20240621.jpg"
        image_file.write_bytes(image_data)
        '''

main()