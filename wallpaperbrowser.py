#! python 3
# -*- coding: UTF-8 -*-

import os
import tkinter.messagebox
from tkinter import *
import asyncio

from PIL import Image, ImageTk
from PIL import ImageFile

from utils import WallpaperDatabase
from dlbingwallpaper import download_image

ImageFile.LOAD_TRUNCATED_IMAGES = True


class App:
    def __init__(self, master, image_path, database):
        self._curr_index = 0
        self._master = None
        self._master = master

        self._image_path = image_path
        self._file_list = os.listdir(self._image_path)
        self._db = database

        if not self._file_list:
            tkinter.messagebox.showinfo('browser', '没找到墙纸！')
            exit(0)

        self._image = Image.open(os.path.join(image_path, self._file_list[self._curr_index]))
        self._image.thumbnail((self._image.width/2, self._image.height/2))
        self._photo_image = ImageTk.PhotoImage(self._image)

        self._label = Label(master, image=self._photo_image)
        self._label.bind("<Double-Button-1>", self.on_label_doubleclick)
        self._label.pack(side=TOP, expand=YES)

        btn_prev = Button(master, text='上一张', fg='green', command=self.on_prev_image)
        self._master.bind('<Left>', self.on_prev_image)
        btn_prev.pack(side=LEFT)

        btn_next = Button(master, text='下一张', fg='green', command=self.on_next_image)
        self._master.bind('<Right>', self.on_next_image)
        btn_next.pack(side=RIGHT)

        self._copyright_text = Message(master,
                                       text=self.get_copyright(self._file_list[self._curr_index]),
                                       width=self._label.winfo_screenwidth())
        self._copyright_text.pack(side=LEFT)
        self._browse_progess_text = Message(master, text=self.get_browse_progress_text(), width=100)
        self._browse_progess_text.pack(anchor=E)

        self._labelmenu_rightclick = Menu(master, tearoff=False)
        self._labelmenu_rightclick.add_command(label='打开路径', command=self.open_path)
        self._labelmenu_rightclick.add_command(label='重新下载（壁纸）', command=self.redownload)
        master.bind("<Button-3>", self.on_label_rightclick)

        self.set_title(self._curr_index)

    def on_label_doubleclick(self, event):
        os.system(os.path.join(self._image_path, self._file_list[self._curr_index]))

    def on_label_rightclick(self, event):
        self._labelmenu_rightclick.post(event.x_root, event.y_root)

    def open_path(self):
        os.system('explorer.exe ' + self._image_path)

    def redownload(self):
        curr_image = self._file_list[self._curr_index]
        url = self._db.get_content_by_startdate(curr_image[:-4], 'fullImageUrl')
        full_name = os.path.join(self._image_path, curr_image)

        copyright_text = self._copyright_text['text']
        self._copyright_text.configure(text='               下载中...', fg='red')
        self._copyright_text.update()
        oldloop = asyncio.get_event_loop()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(asyncio.wait([download_image(url, full_name)]))
        loop.close()
        asyncio.set_event_loop(oldloop)
        self._copyright_text.configure(text=copyright_text, fg='black')
        self._copyright_text.update()

    def on_prev_image(self, event=None):
        if 0 > self._curr_index - 1:
            self._curr_index = len(self._file_list) - 1
        else:
            self._curr_index -= 1

        self.update_image(self._curr_index)

    def on_next_image(self, event=None):
        if len(self._file_list) <= self._curr_index + 1:
            self._curr_index = 0
        else:
            self._curr_index += 1

        self.update_image(self._curr_index)

    def update_image(self, index):
        curr_image = self._file_list[index]
        full_name = os.path.join(self._image_path, curr_image)
        self._image = Image.open(full_name)
        self._image.thumbnail((self._image.width / 2, self._image.height / 2))
        self._photo_image = ImageTk.PhotoImage(self._image)
        self._label.configure(image=self._photo_image)
        self._label.update_idletasks()
        self._copyright_text.configure(text=self.get_copyright(curr_image))
        self._browse_progess_text.configure(text=self.get_browse_progress_text())
        self.set_title(index)

    def set_title(self, index):
        """在标题栏显示图片的日期信息"""
        curr_image = self._file_list[index]
        title_text = ''.join(['本地墙纸浏览', ' : ', curr_image[:-4], '~', self.get_enddate(curr_image)])
        self._master.title(title_text)

    def get_copyright(self, curr_image):
        return self._db.get_content_by_startdate(curr_image[:-4], 'copyright')

    def get_enddate(self, curr_image):
        return self._db.get_content_by_startdate(curr_image[:-4], 'enddate')

    def get_browse_progress_text(self):
        return "{}/{}".format(self._curr_index+1, len(self._file_list))

    def run(self):
        self._master.mainloop()


def main():
    #image_path = r'E:\wallpapers'
    #database_path = r'C:\scripts'

    if len(sys.argv) >= 3 and \
            os.path.isdir(sys.argv[1]) and \
            os.path.isdir(sys.argv[2]):

        image_path = sys.argv[1]
        database_path = sys.argv[2]
    else:
        print('param error.')
        return

    root = Tk()
    root.resizable(width=False, height=False)

    database = WallpaperDatabase(database_path)
    with database.open_db_context():
        app = App(root, image_path, database)
        app.run()


if __name__ == '__main__':
    if sys.version_info.major != 3:
        input("\nPython3 needed!\nPress any key to exit.")
        exit(0)

    main()