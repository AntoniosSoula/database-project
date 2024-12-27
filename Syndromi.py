# Syndromi.py
import sqlite3
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QMessageBox, QInputDialog
from PyQt6.QtCore import Qt

class Syndromi:
    table_name = 'ΣΥΝΔΡΟΜΗ'  # Ή το σωστό όνομα πίνακα για τους συνδρομητές

    def __init__(self, parent):
        self.parent = parent
        self.table = None
        self.table_shown = False
    def show_table(self):
        if self.table_shown:
            self.table.setParent(None)  # Αφαιρούμε τον πίνακα αν έχει εμφανιστεί ήδη
            self.table_shown = False
            
        self.table = QTableWidget()
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {self.table_name}")
        rows = cursor.fetchall()
        conn.close()

        # Αν δεν υπάρχουν δεδομένα, δείχνουμε μήνυμα
        if not rows:
            QMessageBox.warning(self.parent, "Προσοχή", "Δεν υπάρχουν συνδρομητές.")
            return

        # Ρύθμιση του πίνακα
        self.table.setRowCount(len(rows))
        self.table.setColumnCount(len(rows[0]))  # Ο αριθμός των στηλών είναι το μέγεθος της πρώτης γραμμής
        self.table.setHorizontalHeaderLabels(["ID", "Όνομα", "Ημερομηνία Εγγραφής", "Άλλες Στήλες"])  # Εξαρτάται από τις στήλες της βάσης δεδομένων

        # Προσθήκη των δεδομένων στον πίνακα
        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))


        layout = self.parent.tabSyndromi.layout()
        if layout is None:
            layout = QVBoxLayout()
            self.parent.tabSyndromi.setLayout(layout)

        layout.addWidget(self.table)
        self.table_shown = True

