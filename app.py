import sys
from PyQt6.QtWidgets import QApplication, QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QMessageBox
from PyQt6.uic import loadUi
import sqlite3
from PyQt6.QtCore import QDate


# Κλάση για τη διαχείριση των μελών
class Melos:
    def __init__(self, parent):
        self.parent = parent
        self.table = None
        self.table_shown = False

    def show_table(self):
        if self.table_shown:
            self.table.setParent(None)
            self.table_shown = False
        else:
            self.table = QTableWidget()
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ΜΕΛΟΣ")
            rows = cursor.fetchall()
            conn.close()

            self.table.setRowCount(len(rows))
            self.table.setColumnCount(10)  # Προσθήκη στήλης ενημέρωσης
            self.table.setHorizontalHeaderLabels(
                ["Μητρώο Μέλους", "Επώνυμο", "Όνομα", "Ημερομηνία Γέννησης", 
                 "Επίπεδο", "Τηλέφωνο", "Φύλο", "Πλήθος Αδερφών", "Διαγραφή", "Ενημέρωση"]
            )
            for row, row_data in enumerate(rows):
                for column, value in enumerate(row_data):
                    self.table.setItem(row, column, QTableWidgetItem(str(value)))

            # Προσθήκη του πίνακα στο tabMeli
            layout = self.parent.tabMeli.layout() if self.parent.tabMeli.layout() else QVBoxLayout()
            self.parent.tabMeli.setLayout(layout)
            layout.addWidget(self.table)

            self.table_shown = True


# Κύρια κλάση της εφαρμογής
class Main(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("untitled.ui", self)
        self.meli = None  # Αρχικοποιούμε το στιγμιότυπο της κλάσης Meli

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
