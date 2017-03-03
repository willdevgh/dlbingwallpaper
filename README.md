# dlbingwallpaper
Download wallpapers from cn.bing.com.

下载必应壁纸脚本。

# 使用
>`python dlbingwallpaper.py DOWNLOAD_PATH`

例如：

>`python dlbingwallpaper.py E:\wallpapers`

你也可以将脚本的快捷方式放入系统的StartUp下并设置启动参数，作为开机自启动项目。

所有的图片信息保存在数据库wallpaper.db中，可以使用SQLiteStudio查看。

目前表info的path字段未使用。