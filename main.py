import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QScrollArea, QListWidget
from PyQt5.QtCore import Qt
from manga import view_manga_catalog, view_manga_page
import manga_page




class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('Popka')
        self.setGeometry(100,50,600,400)
        self.initUI()
        self.show()

    def initUI(self):

        self.wiget = QWidget()
        self.scrollarea = QScrollArea()
        self.vbox = QVBoxLayout()

        self.catalog = view_manga_catalog()
        self.wiget_list = QListWidget(self)
        for i in self.catalog.keys():
            self.wiget_list.addItem(i)

        self.vbox.addWidget(self.wiget_list)
        self.wiget_list.currentItemChanged.connect(self.selectManga)


        self.wiget.setLayout(self.vbox)

        self.scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollarea.setWidgetResizable(True)
        self.scrollarea.setWidget(self.wiget)

        self.setCentralWidget(self.scrollarea)


    def selectManga(self, item):
        dir, page = self.catalog[item.text()][0], self.catalog[item.text()][1]

        self.window = QWidget()
        self.ui = manga_page.Example()
        self.ui.initUI(self.window)
        self.ui.loadPage(dir, page)
        self.window.show()





if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())


