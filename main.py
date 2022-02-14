import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5 import uic
from manga import view_manga_catalog, view_manga_page, view_manga


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('gui.ui', self)
        self.splitter.setSizes([1,0])
        self.horizontal_splitter.setSizes([1,0])
        self.loadCatalog()
        self.manga_list.itemClicked.connect(self.selectManga)
        self.manga_select_chapter_btn.clicked.connect(self.selectChapter)
        self.manga_branch.itemClicked.connect(self.selectedChapter)
        self.manga_read_btn.clicked.connect(self.readManga)
        self.setCentralWidget(self.stack)
        self.stack.setCurrentIndex(0)
        self.show()

    def loadCatalog(self):
        self.catalog = view_manga_catalog()
        for key in self.catalog.keys():
            self.manga_list.addItem(key)

    def selectManga(self, item):
        self.splitter.setSizes([300,100])
        page_manga = view_manga_page(*self.catalog[item.text()])
        pix = QPixmap(page_manga['img'])
        self.manga_img.setPixmap(pix)
        self.manga_description.setText(page_manga['description'])
        self.branch = page_manga['branch']
        self.dir = page_manga['manga_dir']

    def selectChapter(self):
        self.horizontal_splitter.setSizes([0,1])
        index = 1
        for i in self.branch:
            item = f"{index}. Том {i['tome']}, глава {i['chapter']}."
            self.manga_branch.addItem(item)
            index += 1


    def selectedChapter(self, item):
        self.index_chapter = int(item.text().split('.')[0]) - 1
        print(self.branch[self.index_chapter])

    def readManga(self):
        self.stack.setCurrentIndex(1)
        tome = str(self.branch[self.index_chapter]['tome'])
        chapter = str(self.branch[self.index_chapter]['chapter'])
        name = self.branch[self.index_chapter]['name']
        id = str(self.branch[self.index_chapter]['id'])
        manga_chapter = view_manga(tome, chapter, name, id, self.dir)
        if self.vbox_frames is not None:
            while self.vbox_frames.count():
                child = self.vbox_frames.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
        for frame in manga_chapter[:-1]:
            pix = QPixmap(str(frame))
            lbl = QLabel()
            lbl.setPixmap(pix)
            lbl.setAlignment(Qt.AlignHCenter)
            self.vbox_frames.addWidget(lbl)
        back_btn = QPushButton('Back')
        back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.vbox_frames.addWidget(back_btn)
        self.setMinimumWidth(pix.width())
        self.setMinimumHeight(600)



app = QApplication(sys.argv)
window = MainWindow()
sys.exit(app.exec_())