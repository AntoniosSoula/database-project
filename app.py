import sys
from PyQt6.QtWidgets import (
    QApplication, QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QPushButton, QMessageBox, QInputDialog, QLineEdit, QDateEdit,
)
from PyQt6.uic import loadUi
import sqlite3
from functools import partial
from PyQt6.QtCore import QDate
from ΤableManager import *  # Βεβαιώσου ότι η κλάση TableManager βρίσκεται στο σωστό αρχείο και μονοπάτι

class MyApp(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("untitled.ui", self)
        
        self.buttonTableTeam.clicked.connect(self.show_team_table)
        self.buttonTableNoInTeam.clicked.connect(self.show_no_in_team_table)
        self.buttonTableMeli.clicked.connect(self.show_meli_table)
        
    def show_team_table(self):
        team_manager = TableManager("ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ", ["μητρώο_μέλος", "όνομα", "επώνυμο", "ημερομηνία_γέννησης", "επίπεδο", "τηλέφωνο", "φύλο", "πλήθος_αδελφών"], self)
        team_manager.show_table()

    def show_no_in_team_table(self):
        no_in_team_manager = TableManager("ΞΕΝΟΣ ΠΑΙΚΤΗΣ", ["Μητρώο", "Όνομα", "Επίπεδο", "Διαγραφή", "Ενημέρωση"], self)
        no_in_team_manager.show_table()

    def show_meli_table(self):
        meli_manager = TableManager("ΜΕΛΟΣ", ["μητρώο_μέλος", "όνομα", "επώνυμο", "ημερομηνία_γέννησης", "επίπεδο", "τηλέφωνο", "φύλο", "πλήθος_αδελφών"], self)
        meli_manager.show_table()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)  # Δημιουργία της εφαρμογής πρώτα
    window = MyApp()  # Στη συνέχεια, δημιουργία του παραθύρου
    window.show()
    sys.exit(app.exec())  # Εκκίνηση του event loop
