from view import MainWindow
from PIL import Image


class CatalogController():
    def __init__(self, model, library):
        self.library = library
        self.model = model
        self.view = MainWindow(self, self.model)
        self.view.show()
        self.viewLibrary()
        self.viewCatalog()
        self.viewFilters()


    def viewCatalog(self):
        self.model.initCatalog()
        self.view.initCatalog(self.model.getCatalog())

    def viewPage(self, item):
        if self.view.sender().objectName() == 'search_result_list':
            self.current_page = next(page for page in self.model.getSearchCatalog() if page.name == item.text())
        else:
            self.current_page = next(page for page in self.model.getCatalog() if page.name == item.text())
        self.current_page.initPage()
        self.view.viewSelectManga(self.current_page.loadPageImg())
        #self.view.manga_img.setText(self.current_page.img_url)
        self.view.manga_description.setText(self.current_page.description)
        self.view.manga_select_chapter_btn.setText(f'{self.current_page.branch.count_chapters} глав')

    def viewBranch(self):
        self.view.viewBranchSelectedManga()
        self.current_page.branch.initBranch()
        for i in self.current_page.branch.getBranch():
            item = f"Том {i.tome}, глава {i.chapter}."
            self.view.manga_branch.addItem(item)
            self.view.toolf.tool_branch.addItem(item)

    def selectChapterAndView(self, item):
        index_chapter = self.view.sender().currentRow()
        chapter = self.current_page.branch.getChapter(index_chapter)
        self.viewChapter(chapter)

    def viewChapter(self, chapter):
        self.current_chapter = chapter
        self.current_chapter.initChapter()
        self.view.viewSelectedChapter(self.current_chapter.getFrames())

    def viewNextChapter(self):
        if self.current_chapter.next_chapter:
            chapter = self.current_chapter.nextChapter()
            self.viewChapter(chapter)

    def viewPreviousChapter(self):
        if self.current_chapter.previous_chapter:
            chapter = self.current_chapter.previousChapter()
            self.viewChapter(chapter)

    def changeStackCurentIndex(self):
        cur_index = self.view.stack.currentIndex()
        self.view.stack.setCurrentIndex((cur_index + 1) % self.view.stack.count())

    def enableFilters(self):
        if self.view.main_tool.visible_filters:
            self.view.main_tool.visible_filters = False
            self.view.splitter_tab.setSizes([0, 1])
        else:
            self.view.splitter_tab.setSizes([20, 300])
            self.view.main_tool.visible_filters = True

    def viewFilters(self):
        self.filter = self.model.filters.getAllFilters()
        self.ordering = self.model.ordering.getAllOrdering()
        self.view.filters.initFiltersTab(self.filter, self.ordering)

    def applySelectedFilters(self):
        if not self.view.filters.check_combo_list:
            return
        filters_list = []
        ordering_list = []
        for box in self.view.filters.check_combo_list:
            if box.getCheckedItems() and box[0].text() != 'Сортировка':
                for item in box.getCheckedItems():
                    box.itemUncheck(item)
                    id_filter = next(x['id'] for x in self.filter[box[0].text()] if x["name"] == item.text())
                    filters_list.append([box[0].text(), id_filter])
            else:
                for item in box.getCheckedItems():
                    box.itemUncheck(item)
                    ordering_name = next(k for k, v in self.ordering.items() if v == item.text())
                    ordering_list.append(ordering_name)
        self.view.clearCatalog()
        self.model.clearCatalog()
        self.model.firstPage()
        self.model.filters.buildFilterString(filters_list)
        self.model.ordering.buildOrderingString(ordering_list)
        self.viewCatalog()

    def nextPageCatalog(self, value):
        if value == self.view.manga_list.verticalScrollBar().maximum():
            self.model.nextPage()
            self.viewCatalog()

    def viewSearchCatalog(self):
        search_string = self.view.search.search_line.text()
        self.model.initSearchCatalog(search_string)
        search_catalog = self.model.getSearchCatalog()
        self.view.search.clearSearchCatalog()
        self.view.search.initSearchCatalog(search_catalog)

    def viewLibrary(self):
        self.lib_list = self.library.getLibrary()
        self.model.initLibCatalog(self.lib_list)
        self.lib_catalog = self.model.getLibCatalog()
        for i in self.lib_catalog:
            self.view.library.lib_list.addItem(i.name)

    def addToLibrary(self):
        page_name, page_url = self.current_page.addToLibrary()
        chapter_id = self.current_chapter.addToLibrary()
        self.library.addLibrary([page_name, page_url, chapter_id])

    def saveLibrary(self):
        self.library.saveLibrary()

    def continueReadManga(self, item):
        self.current_page = next(page for page in self.model.getLibCatalog() if page.name == item.text())
        last_chapter = self.lib_list[item.text()]['current_chapter']
        self.current_page.initPage()
        self.viewBranch()
        chapter = next(chapter for chapter in self.current_page.branch.getBranch() if chapter.id == last_chapter)
        self.changeStackCurentIndex()
        self.viewChapter(chapter)