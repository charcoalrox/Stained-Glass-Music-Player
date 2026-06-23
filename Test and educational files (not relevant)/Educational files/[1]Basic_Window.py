# from tutorial: https://www.pythonguis.com/tutorials/creating-your-first-pyqt-window/

import sys # command line args

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")
        button = QPushButton("Press Me!")

        # alternatively, I can do setMinimumSize() and setMaximumSize() instead
        self.setFixedSize(QSize(400, 300)) # If I don't want the window resizable

        self.setCentralWidget(button)


app = QApplication(sys.argv)

window = MainWindow()
window.show() # Windows are hidden by default

app.exec()