import sys
from controller import CatalogController
from model import MangaCatalog
from library import Library
from view import MainWindow
from PyQt5.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)

    model = MangaCatalog()
    library = Library()
    controller = CatalogController(model, library)

    app.installEventFilter(controller.view)

    app.exec_()

if __name__ == '__main__':
    sys.exit( main())
