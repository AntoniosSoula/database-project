import sys
from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6.uic import loadUi
from melos import *
class Main(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("untitled.ui", self)
        self.melos = None  # Αρχικοποιούμε το στιγμιότυπο της κλάσης Meli

        # Συνδέουμε το κουμπί με την μέθοδο
        self.buttonTableMeli.clicked.connect(self.show_member_table)


    def show_member_table(self):
        # Δημιουργία του στιγμιότυπου της κλάσης Meli όταν πατηθεί το κουμπί
        if self.melos is None:
            self.melos = Melos(self)
        self.melos.show_table()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec())
