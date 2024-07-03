from datetime import datetime
from pathlib import Path
from wallpaper_downloader import WallpaperDownloader, logger
from utils.database import WallpaperDatabase

# 设置保存路径
SAVE_DIR = r'D:\wallpapers'


def download_bing_wallpaper(save_dir: str):
    save_dir = Path(save_dir)
    if not save_dir.exists():
        save_dir.mkdir()

    database = WallpaperDatabase(SAVE_DIR)
    downloader = WallpaperDownloader()
    info_list: list = downloader.image_info_list(day_count=8)
    timestr = datetime.now().strftime('%Y%m%d')
    with database.open_db_context():
        for i, info in enumerate(info_list):
            logger.info(f"downloading: {info.copyright}")
            database.save_info(info)
            save_filename = save_dir / f'{timestr}_{i}.jpg'
            WallpaperDownloader.download_image(info.url, str(save_filename))


download_bing_wallpaper(SAVE_DIR)
