import os
import base64
from pathlib import Path
from configparser import ConfigParser
import logging.config

from utils.wallpaper_downloader import WallpaperDownloader
from utils.database import WallpaperDatabase
from utils.email import send_email

SCRIPT_NAME = 'DLBINGWALLPAPER'
CONFIG_FILE = 'config.ini'
LOGGING_CONF = 'logging.conf'

logging.config.fileConfig(f'./{LOGGING_CONF}')
logger = logging.getLogger('main')


def main():
    logger.info(f"{SCRIPT_NAME} start running!")
    
    conf = ConfigParser()
    if not conf.read(Path(os.path.abspath(os.curdir)) / CONFIG_FILE):
        logger.error("config.ini not found!")
        return
    
    # [data_save]
    data_save_section = conf['data_save']
    if not data_save_section:
        logger.error("section 'data_save' not found in config.ini!")
        return
    
    save_path = Path(data_save_section.get('path', fallback=os.curdir))
    save_as_image_file = data_save_section.getboolean('save_as_image_file')

    # [email]
    email_section = conf['email']
    if not email_section:
        logger.error("section 'email' not found in config.ini!")
        return
    
    smtp_host = email_section.get('smtp_host')
    smtp_port = email_section.getint('smtp_port')
    auth_password = email_section.get('auth_password')
    from_mailbox = email_section.get('from')
    to_mailboxes = email_section.get('to').split(',')
    if False in (bool(smtp_host), bool(smtp_port), bool(auth_password), bool(from_mailbox), bool(to_mailboxes)):
        logger.error("parameter missing in config.ini!")
        return

    downloader = WallpaperDownloader()
    database = WallpaperDatabase(str(save_path.absolute()))

    try:
        info_list: list = downloader.image_info_list(day_count=8)

        with database.open_db_context():
            # 下载 & 保存
            for info in info_list:
                logger.info(f"downloading: {info.enddate} {info.copyright}")
                if database.record_exist(info.enddate):
                    logger.info('wallpaper exist, skip.')
                    continue

                image_file = save_path / f"{info.enddate}_{info.title}.jpg"
                downloader.download_image(info.url, image_file)
                data = image_file.read_bytes()
                b64_data = base64.b64encode(data)
                if database.save_info(info, b64_data):
                    send_email(smtp_host, smtp_port, from_mailbox, auth_password, to_mailboxes, f"[Bing今日美图] {info.title}", (image_file, ))
                    logger.info("email has been sent to the specified mailbox.")
                
                if not save_as_image_file:
                    image_file.unlink(missing_ok=True)
    except Exception as e:
        logger.exception(f"exception: \n{e}")
    
    logger.info(f"{SCRIPT_NAME} exit.")

# Run this script
main()
