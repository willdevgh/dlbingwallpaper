#! python 3
# --*-- encoding: UTF-8 --*--

'''
The original source code is: https://github.com/rorschachhb/cleanBingDesktop
'''

import sys
import xml.etree.ElementTree as ET
import os
import os.path as op
import requests
import sqlite3


def download_wallpapers():
    print("\nDownload wallpapers from cn.bing.com\n")

    script_path = os.path.abspath('.')

    save_path = script_path

    if len(sys.argv) >= 2:
        if os.path.isdir(sys.argv[1]):
            save_path = sys.argv[1]

    if not save_path.endswith('\\'):
        save_path += '\\'

    if not script_path.endswith('\\'):
        script_path += '\\'

    # A SQLite database to save every wallpaper's information.
    db_conn = sqlite3.connect(script_path + 'wallpaper.db')
    cu = db_conn.cursor()

    dl_failed = {}
    sv_failed = {}

    if not op.exists(save_path):
        os.mkdir(save_path)

    for i in range(8, -1, -1):
        print("****************************index: %d" % i)
        # download wallpaper's info
        # this url supports ipv6, but cn.bing.com doesn't
        xml_url = 'http://az517271.vo.msecnd.net/TodayImageService.svc/HPImageArchive?mkt=zh-cn&idx=%d' % (i)

        try:
            xml_data = requests.get(xml_url)
            root = ET.fromstring(xml_data.text)
        except requests.exceptions.ConnectionError:
            print("raise ConnectionError while downloading wallpaper's information.")
            dl_failed[i] = xml_url + " $ raise ConnectionError."
            continue

        start_date = root[0].text
        end_date = root[2].text
        full_image_url = root[6].text
        copyright = root[7].text

        print("wallpaper url: [%s]" % full_image_url)
        file_name = start_date + '.jpg'
        save_file_name = op.join(save_path, file_name)
        if not op.exists(save_file_name):
            try:
                image_data = requests.get(full_image_url, stream=True)

                with open(save_file_name, 'wb') as image_file:
                    for chunk in image_data.iter_content(chunk_size=1024):
                        if chunk:  # filter out keep-alive new chunks
                            image_file.write(chunk)
                            image_file.flush()
                    image_file.close()
                    print("Download wallpaper '%s' success!" % file_name)

                    try:
                        # save info
                        cu.execute("INSERT INTO info VALUES('%s', '%s', '%s', '%s')" \
                                   % (start_date, end_date, full_image_url, copyright))
                        db_conn.commit()
                    except sqlite3.IntegrityError:
                        print("raise sqlite3.IntegrityError, duplicate key value violates unique constraint.")
                        sv_failed[i] = full_image_url + " $ raise sqlite3.IntegrityError."

            except requests.exceptions.ConnectionError:
                print("raise ConnectionError while downloading wallpapers.")
                dl_failed[i] = full_image_url + " $ raise ConnectionError."
                continue
        else:
            print("Wallpaper named %s is already exist." % file_name)
            print("You can find it in path '%s'" % save_path)
            dl_failed[i] = full_image_url + " $ already exist."

    db_conn.close()

    print("")
    if not len(dl_failed) == 0:
        print("Following wallpapers were downloaded failed:")
        for k in dl_failed:
            print("index: %d, url: %s" %(k, dl_failed[k]))

        print("Download finished! You will find some of them in path '%s'." % save_path)
    else:
        print("Download finished! You will find all of them in path '%s'." % save_path)

    print("")
    if not len(sv_failed) == 0:
        print("Following infos were saved failed:")
        for k in sv_failed:
            print("index: %d, url: %s" %(k, sv_failed[k]))
    else:
        print("All infos were saved in db!")


    input("\nPress any key to exit.")


download_wallpapers()