import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QAction, QToolBar, QListWidget, QComboBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QEvent
from PyQt5 import uic
from manga import view_manga_catalog, view_manga_page, view_manga, get_filters
from gui import Ui_Form



class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('gui.ui', self)
        self.splitter.setSizes([1,0])
        self.horizontal_splitter.setSizes([1,0])
        self.loadCatalog()
        self.initMainToolbar()
        self.initFramesToolbar()
        self.manga_list.itemClicked.connect(self.selectManga)
        self.manga_select_chapter_btn.clicked.connect(self.selectChapter)
        self.manga_branch.itemClicked.connect(self.selectedChapter)
        self.manga_read_btn.clicked.connect(self.readManga)
        self.setCentralWidget(self.stack)
        self.stack.setCurrentIndex(0)
        self.show()



    def eventFilter(self, source, event):
        if self.stack.currentIndex() == 1 and event.type() == QEvent.MouseMove:
            if event.buttons() == Qt.NoButton:
                if event.windowPos().toPoint().x() >= self.size().width() - 150:
                    self.toolf.show()
                else:
                    self.toolf.hide()
        elif self.stack.currentIndex() == 0:
            self.toolf.hide()
        return super(MainWindow, self).eventFilter(source, event)


    def initMainToolbar(self):
        self.main_tool = QToolBar()
        self.main_tool.setMovable(False)
        btn_filter = QPushButton('Фильтры')
        btn_filter.clicked.connect(self.applyFilters)
        self.main_tool.addWidget(btn_filter)
        self.genres_boxes_builder()
        self.addToolBar(Qt.TopToolBarArea, self.main_tool)


    def initFramesToolbar(self):
        self.toolf = QToolBar()
        self.toolf.setMovable(False)
        self.toolf.setFixedWidth(150)
        btn_back = QPushButton('На главную')
        btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.toolf.addWidget(btn_back)
        self.tool_branch = QListWidget()
        self.tool_branch.itemClicked.connect(self.selectedChapterAndRead)
        self.toolf.addWidget(self.tool_branch)
        btn_previous = QPushButton('Previous')
        btn_previous.clicked.connect(self.previousChapter)
        btn_continue = QPushButton('Continue')
        btn_continue.clicked.connect(self.nextChapter)
        self.toolf.addWidget(btn_previous)
        self.toolf.addWidget(btn_continue)
        self.addToolBar(Qt.RightToolBarArea, self.toolf)



    def loadCatalog(self):
        self.catalog = view_manga_catalog()
        for key in self.catalog.keys():
            self.manga_list.addItem(key)

    def selectManga(self, item):
        self.splitter.setSizes([300,100])
        self.horizontal_splitter.setSizes([1, 0])
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
            self.tool_branch.addItem(item)
            index += 1

    def selectedChapter(self, item):
        self.index_chapter = int(item.text().split('.')[0]) - 1


    def readManga(self):
        self.stack.setCurrentIndex(1)

        tome = str(self.branch[self.index_chapter]['tome'])
        chapter = str(self.branch[self.index_chapter]['chapter'])
        name = self.branch[self.index_chapter]['name']
        manga_id = str(self.branch[self.index_chapter]['id'])
        manga_chapter = view_manga(tome, chapter, name, manga_id, self.dir)
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

    def selectedChapterAndRead(self, item):
        self.selectedChapter(item)
        self.readManga()

    def nextChapter(self):
        if len(self.branch)-1 >= self.index_chapter + 1:
            self.index_chapter += 1
            self.readManga()

    def previousChapter(self):
        if self.index_chapter != 0:
            self.index_chapter -= 1
            self.readManga()

    def genres_boxes_builder(self):
        filters = get_filters()
        for fname, fcontent in filters.items():
            check_combo = CheckableComboBox()
            check_combo.addItem(fname)
            for filter in fcontent:
                check_combo.addItem(filter['name'])
            self.main_tool.addWidget(check_combo)

    def applyFilters(self):
        ass = {}
        for box in self.main_tool.findChildren(CheckableComboBox):
            sd = []
            for i in box.getItems():
                if i.checkState() == Qt.Checked:
                    print(i.text())






class CheckableComboBox(QComboBox):
    def __init__(self, parent=None):
        super(CheckableComboBox, self).__init__(parent)
        self._changed = False
        self.view().pressed.connect(self.handleItemPressed)

    def getItems(self):
        for index in range(self.count()):
            yield self.model().item(index, self.modelColumn())


    def setItemChecked(self, index, checked=False):
        item = self.model().item(index, self.modelColumn())

        if checked:
            item.setCheckState(Qt.Checked)
        else:
            item.setCheckState(Qt.Unchecked)


        self.view().pressed.connect(self.handleItemPressed)

    def handleItemPressed(self, index):
        if index.row() == 0:
            print('ti cho eben')
            return
        item = self.model().itemFromIndex(index)
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)
        self._changed = True

    def hidePopup(self):
        if not self._changed:
            super().hidePopup()
        self._changed = False


    def itemChecked(self, index):
        item = self.model().item(index, self.modelColumn())
        if item.checkState() == Qt.Checked:
            return item.text()


app = QApplication(sys.argv)
window = MainWindow()
app.installEventFilter(window)
sys.exit(app.exec_())