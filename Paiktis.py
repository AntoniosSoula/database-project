import sys
from PyQt6.QtWidgets import QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QMessageBox, QInputDialog
from PyQt6.uic import loadUi
import sqlite3
from PyQt6.QtCore import QDate
from Melos import *

class TeamPaiktis(Melos):
    table_name="ΠΑΙΚΤΗΣ"
    table2_name="ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ"
    def __init__(self, parent):
        super().__init__(parent)

    def show_table(self):
        if self.table_shown:
            self.table.setParent(None)
            self.table_shown = False
        else:
            self.table = QTableWidget()
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            query = f"""
            SELECT "{super().table_name}".*, "{self.table_name}".*, "{self.table2_name}".*
            FROM "{self.table_name}"
            JOIN "{super().table_name}" 
            ON "{self.table_name}"."μητρώο_μέλους" = "{super().table_name}"."μητρώο_μέλους"
            JOIN "{self.table2_name}" 
            ON "{self.table_name}"."μητρώο_μέλους" = "{self.table_name}"."μητρώο_μέλους"
            AND "{self.table2_name}".RN = "{self.table_name}".RN
        """
            cursor.execute(query)
            rows = cursor.fetchall()

        # Λήψη δυναμικών στηλών
            column_names = [description[0] for description in cursor.description]

            conn.close()

        # Ρυθμίσεις για το QTableWidget
            self.table.setRowCount(len(rows))
            self.table.setColumnCount(len(column_names) + 2)  # +2 για τις στήλες Διαγραφή και Ενημέρωση
            self.table.setHorizontalHeaderLabels(column_names + ["Διαγραφή", "Ενημέρωση"])

            for row, row_data in enumerate(rows):
                for column, value in enumerate(row_data):
                    self.table.setItem(row, column, QTableWidgetItem(str(value)))
                
                # Δημιουργία κουμπιού για Διαγραφή και Ενημέρωση για κάθε γραμμή
                delete_button = QPushButton("Διαγραφή")
                update_button = QPushButton("Ενημέρωση")
                # Set the style from the loaded stylesheet

                # Σύνδεση των κουμπιών με τις αντίστοιχες μεθόδους
                delete_button.clicked.connect(lambda checked, row=row: self.delete_member(row))
                update_button.clicked.connect(lambda checked, row=row: self.update_member(row))

                self.table.setCellWidget(row, len(column_names), delete_button)  # Διαγραφή
                self.table.setCellWidget(row, len(column_names) + 1, update_button)
            # Προσθήκη του πίνακα στο tabMeli
            layout = self.parent.tabMeli.layout()
            if layout is None:
                layout = QVBoxLayout()
                self.parent.tabMeli.setLayout(layout)

            layout.addWidget(self.table)
            layout.addWidget(self.backButton)
            self.table_shown = True
            self.addButton = QPushButton("Προσθήκη Παίκτη της Ομάδας")
            self.addButton.setStyleSheet(self.Buttonstylesheet)
            self.addButton.clicked.connect(self.add_member)
            layout.addWidget(self.addButton)
    def add_member(self):
        # Ζήτα από τον χρήστη το μητρώο μέλους
        μητρώο_μέλους, ok1 = QInputDialog.getText(self.parent, "Εισαγωγή Μητρώου Μέλους", "Μητρώο Μέλους:")

        if not ok1:
            QMessageBox.warning(self.parent, "Σφάλμα", "Πρέπει να εισάγεις δεδομένα.")
            return

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Έλεγχος αν υπάρχει το μητρώο_μέλους στον πίνακα "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ"
        cursor.execute("""
            SELECT * FROM "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ"
            WHERE "μητρώο_μέλους" = ?
        """, (μητρώο_μέλους,))
        result = cursor.fetchone()
        
        if result:
            QMessageBox.warning(self.parent, "Σφάλμα", "Ο παίκτης υπάρχει ήδη στην ομάδα.")
            conn.close()
            return

        # Έλεγχος αν υπάρχει το μητρώο_μέλους στον πίνακα "ΞΕΝΟΣ ΠΑΙΚΤΗΣ"
        cursor.execute("""
            SELECT * FROM "ΞΕΝΟΣ ΠΑΙΚΤΗΣ"
            WHERE "μητρώο_μέλους" = ?
        """, (μητρώο_μέλους,))
        result = cursor.fetchone()
        
        if result:
            QMessageBox.warning(self.parent, "Σφάλμα", "Ο παίκτης είναι ξένος και δεν μπορεί να προστεθεί.")
            conn.close()
            return

        # Αν δεν βρέθηκε σε κανέναν από τους πίνακες, ζητείται το RN
        RN, ok2 = QInputDialog.getText(self.parent, "Εισαγωγή RN", "RN:")

        if not ok2:
            QMessageBox.warning(self.parent, "Σφάλμα", "Πρέπει να εισάγεις το RN.")
            conn.close()
            return

        try:
            # Εισαγωγή στον πίνακα "ΠΑΙΚΤΗΣ"
            cursor.execute("""
                INSERT INTO "ΠΑΙΚΤΗΣ" ("RN", "μητρώο_μέλους")
                VALUES (?, ?)
            """, (RN, μητρώο_μέλους))

            # Εισαγωγή στον πίνακα "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ" με αρχικές τιμές για ήττες, νίκες και points
            cursor.execute("""
                INSERT INTO "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ" ("RN", "μητρώο_μέλους", "ήττες", "νίκες", "points")
                VALUES (?, ?, 0, 0, 0)
            """, (RN, μητρώο_μέλους))

            conn.commit()  # Επιβεβαίωση αλλαγών στη βάση
            QMessageBox.information(self.parent, "Επιτυχία", "Ο παίκτης προστέθηκε στην ομάδα.")
            self.show_table()

        except sqlite3.Error as e:
            QMessageBox.critical(self.parent, "Σφάλμα", f"Παρουσιάστηκε σφάλμα κατά την εισαγωγή του παίκτη: {e}")
        
        finally:
            conn.close()
