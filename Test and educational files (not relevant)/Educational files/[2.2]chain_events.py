# From tutorial: https://www.pythonguis.com/tutorials/pyqt-signals-slots-events/

import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        self.label = QLabel() # Text container element

        self.input = QLineEdit() # Input element
        self.input.textChanged.connect(self.label.setText) # Two elements connected. Builtin func

        layout = QVBoxLayout()
        layout.addWidget(self.input)
        layout.addWidget(self.label)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()