from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton,
                             QAction, QToolBar, QListWidget, QComboBox, QVBoxLayout, QLineEdit)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QEvent
from PyQt5 import uic


class MainWindow(QMainWindow):
    def __init__(self, controller, model):
        super(MainWindow, self).__init__()
        self.controller = controller
        self.model = model
        self.screen_size = QApplication.primaryScreen().size()
        uic.loadUi('gui.ui', self)
        self.initUi()
        self.stack.setCurrentIndex(0)
        self.initSignals()

    def eventFilter(self, source, event):
        if self.stack.currentIndex() == 1 and event.type() == QEvent.MouseMove:
            if event.buttons() == Qt.NoButton:
                if event.windowPos().toPoint().x() < 150:
                    self.toolf.show()
                else:
                    self.toolf.hide()
        elif self.stack.currentIndex() == 0:
            self.toolf.hide()
        return super(MainWindow, self).eventFilter(source, event)

    def initUi(self):
        self.splitter.setSizes([1, 0])
        self.splitter_tab.setSizes([0, 1])
        self.horizontal_splitter.setSizes([1, 0])
        self.setCentralWidget(self.stack)
        self.initToolbar()

    def initSignals(self):
        self.manga_list.itemClicked.connect(self.controller.viewPage)
        self.manga_select_chapter_btn.clicked.connect(self.controller.viewBranch)
        self.manga_branch.itemClicked.connect(self.controller.selectChapterAndView)
        self.manga_branch.itemClicked.connect(self.controller.changeStackCurentIndex)
        self.manga_select_chapter_btn.clicked.connect(self.controller.viewBranch)
        self.toolf.tool_branch.clicked.connect(self.controller.selectChapterAndView)
        self.toolf.btn_back.clicked.connect(self.controller.changeStackCurentIndex)
        self.toolf.btn_next.clicked.connect(self.controller.viewNextChapter)
        self.toolf.btn_previous.clicked.connect(self.controller.viewPreviousChapter)


    def initToolbar(self):
        self.toolf = ChapterToolBar()
        self.addToolBar(Qt.LeftToolBarArea, self.toolf)

    def initCatalog(self, catalog_list):
        for i in catalog_list:
            self.manga_list.addItem(i.name)

    def viewSelectManga(self):
        self.splitter.setSizes([300, 100])
        self.horizontal_splitter.setSizes([1, 0])

    def viewBranchSelectedManga(self):
        self.horizontal_splitter.setSizes([0, 1])
        self.manga_branch.clear()

    def viewSelectedChapter(self, frames_list):
        if self.vbox_frames is not None:
            while self.vbox_frames.count():
                child = self.vbox_frames.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()

        for i in frames_list:
            im = QImage(i.image)
            pix = QPixmap.fromImage(im)
            if pix.width() > self.screen_size.width():
                pix.scaledToWidth(self.screen_size.width())
            lbl = QLabel()
            #lbl.setAlignment(Qt.AlignHCenter)
            lbl.setPixmap(pix)
            self.vbox_frames.addWidget(lbl)


class ChapterToolBar(QToolBar):
    def __init__(self, parent=None):
        super(ChapterToolBar, self).__init__(parent)
        self.setMovable(False)
        self.setFixedWidth(150)
        self.btn_back = QPushButton('На главную')
        self.btn_add_read = QPushButton('Добавить в читаемое')
        self.tool_branch = QListWidget()
        self.btn_previous = QPushButton('Предыдущая глава')
        self.btn_next = QPushButton('Следующая глава')
        self.addWidget(self.btn_back)
        self.addWidget(self.btn_add_read)
        self.addWidget(self.tool_branch)
        self.addWidget(self.btn_previous)
        self.addWidget(self.btn_next)


