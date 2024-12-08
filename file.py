from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow

app = QApplication([])

# Φορτώνει το UI από το αρχείο .ui
window = uic.loadUi("untitled.ui")

window.show()
app.exec()