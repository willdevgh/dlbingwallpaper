#! python 3
# -*- coding: UTF-8 -*-

import os
from tkinter import *

from PIL import Image, ImageTk
from PIL import ImageFile

from dlbingwallpaper import WallpaperDatabase
from dlbingwallpaper import download


ImageFile.LOAD_TRUNCATED_IMAGES = True


class App:
    def __init__(self, master, image_path, database):
        self._curr_index = 0
        self._master = None

        self._master = master

        self._image_path = image_path
        self._file_list = os.listdir(self._image_path)
        self._db = database

        self._image = Image.open(os.path.join(image_path, self._file_list[self._curr_index]))
        self._image.thumbnail((self._image.width/2, self._image.height/2))
        self._photo_image = ImageTk.PhotoImage(self._image)

        self._label = Label(master, image=self._photo_image)
        self._label.bind("<Double-Button-1>", self.label_doubleclick)
        self._label.pack(side=TOP, expand=YES)

        btn_prev = Button(master, text='上一张', fg='green', command=self.prev_image)
        self._master.bind('<Left>', self.prev_image)
        btn_prev.pack(side=LEFT)

        btn_next = Button(master, text='下一张', fg='green', command=self.next_image)
        self._master.bind('<Right>', self.next_image)
        btn_next.pack(side=RIGHT)

        self._copyright_text = Message(master, text=self.get_copyright_text(self._file_list[self._curr_index]),
                                       width=self._label.winfo_screenwidth())
        self._copyright_text.pack(side=LEFT)
        self._browse_progess_text = Message(master, text=self.get_browse_progress_text(), width=100)
        self._browse_progess_text.pack(anchor=E)

        self._labelmenu_rightclick = Menu(master, tearoff=False)
        self._labelmenu_rightclick.add_command(label='打开路径', command=self.open_path)
        master.bind("<Button-3>", self.label_rightclick)

    def label_doubleclick(self, event):
        os.system(os.path.join(self._image_path, self._file_list[self._curr_index]))

    def label_rightclick(self, event):
        self._labelmenu_rightclick.post(event.x_root, event.y_root)

    def open_path(self):
        os.system('explorer.exe ' + self._image_path)

    # 暂未使用
    def redownload(self):
        curr_image = self._file_list[self._curr_index]
        url = self._db.get_fullImageUrl(curr_image[:-4])
        full_name = os.path.join(self._image_path, curr_image)
        download(url, full_name)

    def prev_image(self, event=None):
        if 0 > self._curr_index - 1:
            self._curr_index = len(self._file_list) - 1
        else:
            self._curr_index -= 1

        self.update_image(self._curr_index)

    def next_image(self, event=None):
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
        self._copyright_text.configure(text=self.get_copyright_text(curr_image))
        self._browse_progess_text.configure(text=self.get_browse_progress_text())

    def get_copyright_text(self, curr_image):
        return self._db.get_copyright(curr_image[:-4])

    def get_browse_progress_text(self):
        return "{}/{}".format(self._curr_index+1 , len(self._file_list))

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
    root.title("本地墙纸浏览")
    root.resizable(width=False, height=False)

    database = WallpaperDatabase(database_path)
    with database.open_db_context():
        app = App(root, image_path, database)
        app.run()


if __name__ == '__main__':
    if sys.version_info.major != 3:
        input('\nPython3 needed!\nPress any key to exit.')
        exit(0)

    main()
