# Syndromi.py
import sqlite3
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QMessageBox, QInputDialog
from PyQt6.QtCore import Qt

class Syndromi:
    table_name = 'ΣΥΝΔΡΟΜΗΤΗΣ'  # Ή το σωστό όνομα πίνακα για τους συνδρομητές

    def __init__(self, parent):
        self.parent = parent
        self.table = QTableWidget()

    def show_table(self):
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

        # Προσθήκη κουμπιών "Διαγραφή" και "Ενημέρωση" για κάθε γραμμή
        for row_idx in range(len(rows)):
            delete_button = QPushButton("Διαγραφή")
            update_button = QPushButton("Ενημέρωση")
            self.table.setCellWidget(row_idx, len(row_data), delete_button)  # Στήλη για Διαγραφή
            self.table.setCellWidget(row_idx, len(row_data)+1, update_button)  # Στήλη για Ενημέρωση

            # Σύνδεση κουμπιών με τις μεθόδους για διαγραφή και ενημέρωση
            delete_button.clicked.connect(lambda checked, row=row_idx: self.delete_subscription(row))
            update_button.clicked.connect(lambda checked, row=row_idx: self.update_subscription(row))

        layout = self.parent.tabSyndromi.layout()
        if layout is None:
            layout = QVBoxLayout()
            self.parent.tabSyndromi.setLayout(layout)

        layout.addWidget(self.table)

    def delete_subscription(self, row):
        item = self.table.item(row, 0)
        if item:
            subscription_id = item.text()
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {self.table_name} WHERE id = ?", (subscription_id,))
            conn.commit()
            conn.close()
            self.table.removeRow(row)
            QMessageBox.information(self.parent, "Επιτυχία", f"Ο συνδρομητής με ID {subscription_id} διαγράφηκε.")

    def update_subscription(self, row):
        subscription_id = self.table.item(row, 0).text()
        new_value, ok = QInputDialog.getText(self.parent, "Νέα Τιμή", "Εισάγετε νέα τιμή για το όνομα:")
        if ok:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute(f"UPDATE {self.table_name} SET name = ? WHERE id = ?", (new_value, subscription_id))
            conn.commit()
            conn.close()
            self.table.setItem(row, 1, QTableWidgetItem(new_value))
            QMessageBox.information(self.parent, "Επιτυχία", "Τα δεδομένα ενημερώθηκαν επιτυχώς.")
