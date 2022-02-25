from view import MainWindow
from PIL import Image


class CatalogController():
    def __init__(self, model):
        self.model = model
        self.view = MainWindow(self, self.model)
        self.view.show()
        self.viewCatalog()


    def viewCatalog(self):
        self.model.initCatalog()
        self.view.initCatalog(self.model.getCatalog())


    def viewPage(self, item):
        self.current_page = next(page for page in self.model.catalog_list if page.name == item.text())
        self.current_page.initPage()
        self.view.viewSelectManga()
        self.view.manga_img.setText(self.current_page.img_url)
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

