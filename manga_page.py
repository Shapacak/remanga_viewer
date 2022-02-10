import sys
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QMetaObject, QCoreApplication, QMutex
from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel,
                              QVBoxLayout, QListWidget, QTextEdit, QHBoxLayout)
from manga import view_manga_page
from frame_viewer import FrameViewer

class Example(object):
    def loadPage(self, dir, page):
        self.dir = dir
        page = view_manga_page(self.dir, page)
        description = page['description']
        img = page['img']
        self.branch = page['branch']
        index_chapter = 1
        self.lbl.setPixmap(QPixmap(img))
        self.txt_edit.setText(description)
        for i in self.branch:
            lbl = f"{index_chapter}.Том {i['tome']}, глава {i['chapter']}"
            self.list_chapter.addItem(lbl)
            index_chapter+=1

    def initUI(self, Form):

        self.widget = QWidget(Form)
        self.hbox = QHBoxLayout(self.widget)
        self.vbox = QVBoxLayout()

        self.lbl = QLabel()
        self.lbl.setPixmap(QPixmap('pic/icon.png'))
        self.vbox.addWidget(self.lbl)

        self.btn = QPushButton('Read')
        self.vbox.addWidget(self.btn)

        self.txt_edit = QTextEdit()
        self.txt_edit.setReadOnly(True)
        self.hbox.addWidget(self.txt_edit)

        self.list_chapter = QListWidget()
        self.hbox.addWidget(self.list_chapter)
        self.list_chapter.currentItemChanged.connect(self.selectChapter)

        self.hbox.addLayout(self.vbox)
        self.widget.setMinimumWidth(800)
        self.widget.setMinimumHeight(400)
        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)



    def selectChapter(self, item):
        index = int(item.text().split('.')[0]) - 1
        select_chapter = self.branch[index]

        self.window = QWidget()
        self.ui = FrameViewer()
        self.ui.initUI(self.window)
        self.ui.loadFrames(str(select_chapter['tome']), str(select_chapter['chapter']), select_chapter['name'], str(select_chapter['id']), self.dir)




    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Страница"))
        self.lbl.setText(QCoreApplication.translate("Form", u"Картинка"))
        self.btn.setText(QCoreApplication.translate("Form", u"Читать"))

