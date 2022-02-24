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
        self.selected_page = next(page for page in self.model.catalog_list if page.name == item.text())
        self.selected_page.initPage()
        self.view.viewSelectManga()
        self.view.manga_img.setText(self.selected_page.img_url)
        self.view.manga_description.setText(self.selected_page.description)
        self.view.manga_select_chapter_btn.setText(f'{self.selected_page.branch.count_chapters} глав')

    def viewBranch(self):
        self.view.viewBranchSelectedManga()
        index = 1
        for i in self.selected_page.branch.getBranch():
            item = f"{index}. Том {i.tome}, глава {i.chapter}."
            self.view.manga_branch.addItem(item)
            self.view.toolf.tool_branch.addItem(item)

    def viewChapter(self, item):
        index_chapter = int(item.text().split('.')[0])
        chapter = self.selected_page.branch.chapters_list[index_chapter]
        chapter.initChapter()
        self.frames_list = chapter.getFrames()
        self.view.viewSelectedChapter()


    def clickBack(self):
        self.view.stack.setCurrentIndex(0)
