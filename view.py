from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton,
                             QAction, QToolBar, QListWidget, QComboBox, QVBoxLayout, QWidget, QLineEdit)
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

    def closeEvent(self, event):
        self.controller.saveLibrary()
        event.accept()

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
        self.initLibraryCatalog()
        self.initMainToolbar()
        self.initChapterToolbar()
        self.initFiltersTab()
        self.initSearchTab()

    def initSignals(self):
        self.manga_list.itemClicked.connect(self.controller.viewPage)
        self.manga_list.verticalScrollBar().valueChanged.connect(self.controller.nextPageCatalog)
        self.manga_select_chapter_btn.clicked.connect(self.controller.viewBranch)
        self.manga_branch.itemClicked.connect(self.controller.selectChapterAndView)
        self.manga_branch.itemClicked.connect(self.controller.changeStackCurentIndex)
        self.manga_select_chapter_btn.clicked.connect(self.controller.viewBranch)
        self.main_tool.filters_action.triggered.connect(self.controller.enableFilters)
        self.toolf.tool_branch.clicked.connect(self.controller.selectChapterAndView)
        self.toolf.btn_back.clicked.connect(self.controller.changeStackCurentIndex)
        self.toolf.btn_add_read.clicked.connect(self.controller.addToLibrary)
        self.toolf.btn_next.clicked.connect(self.controller.viewNextChapter)
        self.toolf.btn_previous.clicked.connect(self.controller.viewPreviousChapter)
        self.filters.btn_apply.clicked.connect(self.controller.applySelectedFilters)
        self.search.search_btn.clicked.connect(self.controller.viewSearchCatalog)
        self.search.search_result_list.itemClicked.connect(self.controller.viewPage)
        self.library.lib_list.itemClicked.connect(self.controller.continueReadManga)


    def initMainToolbar(self):
        self.main_tool = MainPageToolBar()
        self.addToolBar(Qt.TopToolBarArea, self.main_tool)

    def initChapterToolbar(self):
        self.toolf = ChapterToolBar()
        self.addToolBar(Qt.LeftToolBarArea, self.toolf)

    def initFiltersTab(self):
        self.filters = FiltersTab()
        self.tabWidget.addTab(self.filters, 'Фильтры')

    def initSearchTab(self):
        self.search = SearchTab()
        self.tabWidget.addTab(self.search, 'Поиск')

    def initCatalog(self, catalog_list):
        for i in catalog_list:
            self.manga_list.addItem(i.name)

    def clearCatalog(self):
        self.manga_list.clear()

    def initLibraryCatalog(self):
        self.library = LibraryCatalog()
        self.tabWidget.addTab(self.library, 'Подписки')


    def viewSelectManga(self, img):
        self.splitter.setSizes([300, 100])
        self.horizontal_splitter.setSizes([1, 0])
        size = self.widget.sizeHint()
        print(size.width())
        im = QImage(img)
        pix = QPixmap.fromImage(im).scaledToWidth(size.width())
        self.manga_img.setPixmap(pix)

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


class MainPageToolBar(QToolBar):
    def __init__(self, parent=None):
        super(MainPageToolBar, self).__init__(parent)
        self.setMovable(False)
        self.visible_filters = False
        self.filters_action = QAction('Filters', self)
        self.addAction(self.filters_action)


class FiltersTab(QWidget):
    def __init__(self, parent=None):
        super(FiltersTab, self).__init__(parent)
        self.check_combo_list = []
        self.filters_layout = QVBoxLayout()
        self.setLayout(self.filters_layout)
        self.btn_apply = QPushButton('Принять')

    def initFiltersTab(self, filters_dict, ordering_dict):
        for key in filters_dict:
            check_combo = CheckableComboBox()
            check_combo.addItem(key)
            for i in filters_dict[key]:
                check_combo.addItem(i['name'])
            self.check_combo_list.append(check_combo)
            self.filters_layout.addWidget(check_combo)
        check_combo = CheckableComboBox()
        check_combo.addItem('Сортировка')
        for k, v in ordering_dict.items():
            check_combo.addItem(v)
        self.check_combo_list.append(check_combo)
        self.filters_layout.addWidget(check_combo)
        self.filters_layout.addWidget(self.btn_apply)


class SearchTab(QWidget):
    def __init__(self, parent=None):
        super(SearchTab, self).__init__(parent)
        self.search_layout = QVBoxLayout()
        self.search_line = QLineEdit()
        self.search_btn = QPushButton('Поиск')
        self.search_result_list = QListWidget()
        self.search_result_list.setObjectName('search_result_list')
        self.search_layout.addWidget(self.search_line)
        self.search_layout.addWidget(self.search_btn)
        self.search_layout.addWidget(self.search_result_list)
        self.setLayout(self.search_layout)

    def initSearchCatalog(self, search_catalog_dict):
        self.search_result_list.clear()
        for i in search_catalog_dict:
            self.search_result_list.addItem(i.name)

    def clearSearchCatalog(self):
        self.search_result_list.clear()
        self.search_line.clear()


class LibraryCatalog(QWidget):
    def __init__(self, parent=None):
        super(LibraryCatalog, self).__init__(parent)
        self.lib_vbox = QVBoxLayout()
        self.lib_list = QListWidget()
        self.lib_list.setObjectName('lib_list')
        self.lib_vbox.addWidget(self.lib_list)
        self.setLayout(self.lib_vbox)

        def initLibrary(self, lib_catalog):
            if lib_catalog:
                for name in self.lib_catalog:
                    self.lib_list.addItem(name)


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

    def itemCheck(self, item):
        item.setCheckState(Qt.Checked)
        self._checked.append(item)

    def itemUncheck(self, item):
        item.setCheckState(Qt.Unchecked)
        self._checked.remove(item)

    def handleItemPressed(self, index):
        if index.row() == 0:
            print('ti cho eben')
            return
        item = self.model().itemFromIndex(index)
        if item.checkState() == Qt.Checked:
            self.itemUncheck(item)
        else:
            self.itemCheck(item)
        self._changed = True

    def hidePopup(self):
        if not self._changed:
            super().hidePopup()
        self._changed = False

    def itemChecked(self, index):
        item = self.model().item(index, self.modelColumn())
        if item.checkState() == Qt.Checked:
            return item.text()

