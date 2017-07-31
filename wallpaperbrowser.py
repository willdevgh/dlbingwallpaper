#! python 3
# -*- coding: UTF-8 -*-

import os
from tkinter import *
import tkinter.messagebox
from PIL import Image, ImageTk
from PIL import ImageFile
import sqlite3


ImageFile.LOAD_TRUNCATED_IMAGES = True


class App:
    def __init__(self, master, image_path, datebase_path):
        self.image_path = image_path
        self.file_list = os.listdir(self.image_path)
        self.db_conn = sqlite3.connect(os.path.join(datebase_path, 'wallpaper.db'))

        self.image = Image.open(os.path.join(image_path, self.file_list[0]))
        self.image.thumbnail((self.image.width/2, self.image.height/2))
        self.photo_image = ImageTk.PhotoImage(self.image)
        self.label = Label(master, image=self.photo_image)
        self.label.grid(row=0, columnspan=2)

        self.btn_prev = Button(master, text='上一张', fg='green', command=self.prev_image)
        self.btn_prev.grid(row=1, column=0, sticky=W)

        self.btn_next = Button(master, text='下一张', fg='green', command=self.next_image)
        self.btn_next.grid(row=1, column=1, sticky=E)

        self.image_info_text = Message(master, text=self.get_copyright_text(self.file_list[0]), width=self.label.winfo_screenwidth())
        self.image_info_text.grid(row=2, column=0, sticky=W)

    def prev_image(self):
        if 0 > self.__curr_index - 1:
            print('out of range, index is too small.')
            tkinter.messagebox.showinfo('消息', '已经是第一张了')
            return

        self.__curr_index -= 1
        self.update_image(self.__curr_index)

    def next_image(self):
        if len(self.file_list) <= self.__curr_index + 1:
            print('out of range, index is too large.')
            tkinter.messagebox.showinfo('消息', '已经是最后一张了')
            return

        self.__curr_index += 1
        self.update_image(self.__curr_index)

    def update_image(self, index):
        curr_image = self.file_list[index]
        full_name = os.path.join(self.image_path, curr_image)
        self.image = Image.open(full_name)
        self.image.thumbnail((self.image.width / 2, self.image.height / 2))
        self.photo_image = ImageTk.PhotoImage(self.image)
        self.label.configure(image=self.photo_image)
        self.label.update_idletasks()
        self.image_info_text.configure(text=self.get_copyright_text(curr_image))

    def get_copyright_text(self, curr_image):
        sql = "SELECT copyright FROM info WHERE startdate='{}'".format(curr_image[:-4])
        copyright_text = 'not found!'
        cu = self.db_conn.cursor()
        cu.execute(sql)
        r = cu.fetchall()
        if len(r) > 0:
            copyright_text = r[0][0]

        return copyright_text

    __curr_index = 0


def main():
    image_path = os.path.abspath('.')
    database_path = os.path.abspath('.')

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

    app = App(root, image_path, database_path)

    root.mainloop()


if __name__ == '__main__':
    main()