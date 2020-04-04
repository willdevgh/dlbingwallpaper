#! python 3
# -*- coding: UTF-8 -*-

import sys

from PyQt5.QtWidgets import QMainWindow, QApplication

from ui.mainwindow import Ui_MainWindow


class WallpaperBrowser(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


if __name__ == '__main__':
    if sys.version_info.major != 3:
        input("\nPython3 needed!\nPress any key to exit.")
        exit(0)
    app = QApplication(sys.argv)
    browser = WallpaperBrowser()
    browser.show()
    sys.exit(app.exec_())
