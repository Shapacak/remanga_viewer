import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton,
                             QAction, QToolBar, QListWidget, QComboBox, QVBoxLayout, QLineEdit)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QEvent
from PyQt5 import uic
from manga import view_manga_catalog, view_manga_page, view_manga, get_filters, filters_string_builder, get_search_catalog
from gui import Ui_Form



class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('gui.ui', self)
        self.initUi()
        self.stack.setCurrentIndex(0)
        self.show()

    def initUi(self):
        self.splitter.setSizes([1, 0])
        self.splitter_tab.setSizes([0, 1])
        self.horizontal_splitter.setSizes([1, 0])
        self.initMainToolbar()
        self.initFiltersTab()
        self.initSearchTab()
        self.initFramesToolbar()
        self.loadCatalog()
        self.manga_list.itemClicked.connect(self.selectManga)
        self.manga_select_chapter_btn.clicked.connect(self.selectChapter)
        self.manga_branch.itemClicked.connect(self.selectedChapter)
        self.manga_read_btn.clicked.connect(self.readManga)
        self.setCentralWidget(self.stack)

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
        self.visible_filters = False
        filters_action = QAction('Filters', self)
        filters_action.triggered.connect(self.enableFilters)
        self.main_tool.addAction(filters_action)
        self.addToolBar(Qt.TopToolBarArea, self.main_tool)

    def initFiltersTab(self):
        self.ordering = {'id': 'по новизне', 'chapter_date': 'по последним обновлениям', 'rating': 'по популярности',
                    'votes': 'по лайкам', 'views': 'по просмотрам', 'count_chapters': 'по колличеству глав', 'random': 'случайно'}
        filters_layout = QVBoxLayout()
        self.check_combo_list = []
        self.filters_dict = get_filters()
        for key in self.filters_dict:
            check_combo = CheckableComboBox()
            check_combo.addItem(key)
            for i in self.filters_dict[key]:
                check_combo.addItem(i['name'])
            self.check_combo_list.append(check_combo)
            filters_layout.addWidget(check_combo)
        check_combo = CheckableComboBox()
        check_combo.addItem('Сортировка')
        for k, v in self.ordering.items():
            check_combo.addItem(v)
        self.check_combo_list.append(check_combo)
        filters_layout.addWidget(check_combo)
        btn_apply = QPushButton('Принять')
        btn_apply.clicked.connect(self.applyFilters)
        filters_layout.addWidget(btn_apply)
        self.filters_tab.setLayout(filters_layout)

    def initSearchTab(self):
        search_layout = QVBoxLayout()
        self.search_line = QLineEdit()
        search_btn = QPushButton('Поиск')
        search_btn.clicked.connect(self.getSearchCatalog)
        self.search_result_list = QListWidget()
        self.search_result_list.setObjectName('search_result_list')
        self.search_result_list.itemClicked.connect(self.selectManga)
        search_layout.addWidget(self.search_line)
        search_layout.addWidget(search_btn)
        search_layout.addWidget(self.search_result_list)
        self.search_tab.setLayout(search_layout)


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
        self.manga_list.clear()
        self.catalog = view_manga_catalog()
        for key in self.catalog.keys():
            self.manga_list.addItem(key)

    def selectManga(self, item):
        sender = self.sender().objectName()
        if sender == 'search_result_list':
            view = self.search_catalog[item.text()]
        else:
            view = self.catalog[item.text()]
        self.splitter.setSizes([300,100])
        self.horizontal_splitter.setSizes([1, 0])
        page_manga = view_manga_page(*view)
        pix = QPixmap(page_manga['img'])
        self.manga_img.setPixmap(pix)
        self.manga_description.setText(page_manga['description'])
        self.branch = page_manga['branch']
        self.dir = page_manga['manga_dir']

    def selectChapter(self):
        self.horizontal_splitter.setSizes([0,1])
        self.manga_branch.clear()
        self.tool_branch.clear()
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

    def enableFilters(self):
        if self.visible_filters:
            self.visible_filters = False
            self.splitter_tab.setSizes([0,1])
        else:
            self.splitter_tab.setSizes([20, 300])
            self.visible_filters = True

    def applyFilters(self):
        if not self.check_combo_list:
            return
        filters_list = []
        for box in self.check_combo_list:
            if box.getCheckedItems() and box[0].text() != 'Сортировка':
                for item in box._checked:
                    id_filter = next(x['id'] for x in self.filters_dict[box[0].text()] if x["name"] == item.text())
                    filters_list.append([box[0].text(), id_filter])
            else:
                for item in box._checked:
                    ordering_name = next(k for k,v in self.ordering.items() if v == item.text())
                    filters_list.append(ordering_name)

        if filters_list:
            self.manga_list.clear()
            fstr = filters_string_builder(filters_list)
            self.catalog = view_manga_catalog(filter_string=fstr)
            for key in self.catalog.keys():
                self.manga_list.addItem(key)
        else:
            self.loadCatalog()

    def getSearchCatalog(self):
        self.search_catalog = get_search_catalog(self.search_line.text())
        for key in self.search_catalog.keys():
            self.search_result_list.addItem(key)

class CheckableComboBox(QComboBox):
    def __init__(self, parent=None):
        super(CheckableComboBox, self).__init__(parent)
        self._changed = False
        self._checked = []
        self.view().pressed.connect(self.handleItemPressed)

    def __getitem__(self, index):
        item = self.model().item(index, self.modelColumn())
        return item

    def __iter__(self):
        for index in range(self.count()):
            yield self.model().item(index, self.modelColumn())

    def getCheckedItems(self):
        return self._checked

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
            self._checked.remove(item)
        else:
            item.setCheckState(Qt.Checked)
            self._checked.append(item)
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