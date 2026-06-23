# From tutorial: https://www.pythonguis.com/tutorials/pyqt-signals-slots-events/

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.button_is_checked = True # Set val == to default setCheckable val

        self.setWindowTitle("My App")

        button = QPushButton("Press Me!")
        # button.setCheckable(True) # Whether or not button is blue

        button.clicked.connect(self.the_button_was_clicked) 
        button.clicked.connect(self.the_button_was_toggled) 

        button.setChecked(self.button_is_checked)

        self.setCentralWidget(button)
    
    # Print on button click
    def the_button_was_clicked(self):
        print("clicked!")

    # Toggle true/false based on if button clicked (from internal val, not the variable)
    def the_button_was_toggled(self, checked):
        self.button_is_checked = checked

        print("Checked?", checked)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()