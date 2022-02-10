import sys
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QMetaObject, QCoreApplication, QMutex
from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel,
                              QVBoxLayout, QListWidget, QTextEdit, QHBoxLayout,
                             QApplication, QScrollArea, QSizePolicy)
from manga import view_manga


class FrameViewer(object):
    def initUI(self, Form):

        self.scrollarea = QScrollArea()
        self.vbox = QVBoxLayout(Form)

        Form.setLayout(self.vbox)
        self.scrollarea.setWidget(Form)
        self.scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollarea.setWidgetResizable(True)
        self.scrollarea.move(300,50)
        self.scrollarea.show()

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)


    def loadFrames(self, tome, chapter, name, idm, dir):
        frames = view_manga(tome, chapter, name, idm, dir)
        for frame in frames[:-1]:
            pixmap = QPixmap(str(frame))
            lbl = QLabel()
            lbl.setPixmap(pixmap)
            self.vbox.addWidget(lbl)

        self.scrollarea.setMinimumWidth(pixmap.width())
        self.scrollarea.setMinimumHeight(600)
        print('gotovo')

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Страница"))

