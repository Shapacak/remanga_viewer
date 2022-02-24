import sys
from controller import CatalogController
from model import MangaCatalog
from view import MainWindow
from PyQt5.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)

    model = MangaCatalog()
    controller = CatalogController(model)

    app.installEventFilter(controller.view)

    app.exec_()

if __name__ == '__main__':
    sys.exit( main())
