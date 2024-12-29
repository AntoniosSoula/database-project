import sqlite3
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QMessageBox, QInputDialog,QComboBox
from PyQt6.QtCore import Qt
from Melos import *
from PyQt6.QtGui import QColor
import re
from Prosopiko import *
from Melos import *
class ProponitisProponeiMelos(Prosopiko, Melos):
    table_name = 'ΠΡΟΠΟΝΗΤΗΣ_ΠΡΟΠΟΝΕΙ_ΜΕΛΟΣ'

    def __init__(self, parent):
        Prosopiko.__init__(self, parent)
        Melos.__init__(self, parent)
        self.current_page = 0  # Αρχική σελίδα
        self.rows_per_page = 50  # Αριθμός εγγραφών ανά σελίδα

    def go_back(self):
        if self.table_shown:
            self.table.setParent(None)
            self.backButton.setParent(None)
            self.table_shown = False
            layout = self.parent.tabParousiologio.layout()
            if layout is not None:
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
            self.parent.buttonParousiologio.setEnabled(True)

    def show_table(self):
        query = (f"""SELECT "{self.table_name}"."email",
            "{self.table_name}"."μητρώο_μέλους",
            "{Melos.table_name}"."όνομα",
            "{Melos.table_name}"."επώνυμο",
            "{self.table_name}"."ημερομηνία προπόνησης",
            "{self.table_name}"."κατάσταση"
        FROM 
            "{self.table_name}"
        JOIN 
            "{Melos.table_name}"
        ON 
            "{Melos.table_name}"."μητρώο_μέλους" = "{self.table_name}"."μητρώο_μέλους"
        JOIN 
            "{Prosopiko.table2_name}"
        ON 
            "{Prosopiko.table2_name}"."email" = "{self.table_name}"."email"
        ORDER BY 
          "{self.table_name}"."ημερομηνία προπόνησης" DESC
        LIMIT {self.rows_per_page} OFFSET {self.current_page * self.rows_per_page}""")

        if self.table_shown:
            self.table.setParent(None)
            self.table_shown = False

        self.table = QTableWidget()
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Προπονητής", "Μητρώο Μέλους", "Όνομα", "Επώνυμο",
            "Ημερομηνία Προπόνησης", "Κατάσταση", "Διαγραφή"
        ])

        for row, row_data in enumerate(rows):
            for column, value in enumerate(row_data):
                self.table.setItem(row, column, QTableWidgetItem(str(value)))

            delete_button = QPushButton("Διαγραφή")
            delete_button.setStyleSheet(self.Buttonstylesheet)
            delete_button.clicked.connect(lambda checked, row=row: self.delete_entry(row))
            self.table.setCellWidget(row, 6, delete_button)

        layout = self.parent.tabParousiologio.layout()
        if layout is None:
            layout = QVBoxLayout()
            self.parent.tabParousiologio.setLayout(layout)

        layout.addWidget(self.table)

        # Κουμπιά πλοήγησης
        self.add_navigation_buttons(layout)

        layout.addWidget(self.backButton)
        self.table_shown = True

    def add_navigation_buttons(self, layout):
            # Αφαιρούμε τυχόν προηγούμενα κουμπιά πλοήγησης από το layout
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, QPushButton) and widget.text() in ["Προηγούμενη Σελίδα", "Επόμενη Σελίδα"]:
                layout.takeAt(i).widget().deleteLater()
        # Προηγούμενη Σελίδα
        prev_button = QPushButton("Προηγούμενη Σελίδα")
        prev_button.setStyleSheet(self.Buttonstylesheet)
        prev_button.clicked.connect(self.prev_page)
        prev_button.setEnabled(self.current_page > 0)

        # Επόμενη Σελίδα
        next_button = QPushButton("Επόμενη Σελίδα")
        next_button.setStyleSheet(self.Buttonstylesheet)
        next_button.clicked.connect(self.next_page)

        layout.addWidget(prev_button)
        layout.addWidget(next_button)

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.show_table()

    def next_page(self):
        self.current_page += 1
        self.show_table()


    def delete_entry(self, row):
        item = self.table.item(row, 1)
        if item is None:
            QMessageBox.warning(self.parent, "Σφάλμα", "Δεν βρέθηκε το στοιχείο για διαγραφή.")
            return

        member_id = item.text()
        date_item = self.table.item(row, 4)
        coach_email_item = self.table.item(row, 0)

        if not (coach_email_item and date_item):
            QMessageBox.warning(self.parent, "Σφάλμα", "Λείπουν δεδομένα για τη διαγραφή.")
            return

        coach_email = coach_email_item.text()
        date = date_item.text()

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        try:
            cursor.execute(f"""
                DELETE FROM "{self.table_name}"
                WHERE "email" = ? AND "μητρώο_μέλους" = ? AND "ημερομηνία προπόνησης" = ?
            """, (coach_email, member_id, date))
            conn.commit()

            self.table.blockSignals(True)  # Απενεργοποίηση προσωρινών σημάτων για ταχύτερη ενημέρωση
            self.table.removeRow(row)
            self.table.blockSignals(False)  # Επανενεργοποίηση σημάτων
            QMessageBox.information(self.parent, "Επιτυχία", "Η καταχώρηση διαγράφηκε με επιτυχία.")

        except sqlite3.Error as e:
            QMessageBox.critical(self.parent, "Σφάλμα", f"Σφάλμα κατά τη διαγραφή: {e}")
            conn.rollback()
        finally:
            conn.close()


    def add_presence(self):
        # Δημιουργία διαλόγου επιλογής email
        dialog = QDialog(self.parent)
        dialog.setWindowTitle("Επιλογή Email")
        layout = QVBoxLayout(dialog)

        combo_box = QComboBox(dialog)

        # Φόρτωση emails από τη βάση δεδομένων
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute(f"SELECT email FROM '{Prosopiko.table2_name}'")  # Υποθέτουμε ότι ο πίνακας ονομάζεται 'Προπονητής'
            emails = cursor.fetchall()
            for email in emails:
                combo_box.addItem(email[0])
        except sqlite3.Error as e:
            QMessageBox.critical(self.parent, "Σφάλμα", f"Σφάλμα κατά τη φόρτωση των email: {e}")
        finally:
            conn.close()

        layout.addWidget(combo_box)

        # Κουμπί επιβεβαίωσης
        confirm_button = QPushButton("Επιλογή", dialog)
        layout.addWidget(confirm_button)

        # Σύνδεση του κουμπιού με τη λήψη του επιλεγμένου email
        def confirm():
            email = combo_box.currentText()
            if not email:
                QMessageBox.warning(self.parent, "Σφάλμα", "Δεν επιλέξατε email.")
                return
            dialog.accept()  # Κλείσιμο του διαλόγου

        confirm_button.clicked.connect(confirm)
        dialog.setLayout(layout)
        dialog.exec()

        # Αν δεν επιλέχθηκε email, επιστρέφουμε
        email = combo_box.currentText()
        if not email:
            return

        # Συνεχίζουμε με τα υπόλοιπα δεδομένα
        name, ok2 = QInputDialog.getText(self.parent, "Όνομα", "Εισάγετε το όνομα του υπαλλήλου:")
        if not ok2 or not name:
            return

        surname, ok3 = QInputDialog.getText(self.parent, "Επώνυμο", "Εισάγετε το επώνυμο του υπαλλήλου:")
        if not ok3 or not surname:
            return

        afm, ok4 = QInputDialog.getText(self.parent, "ΑΦΜ", "Εισάγετε το ΑΦΜ (9 ψηφία):")
        if not ok4 or not (len(afm) == 9 and afm.isdigit()):
            QMessageBox.warning(self.parent, "Σφάλμα", "Το ΑΦΜ πρέπει να αποτελείται από 9 ψηφία.")
            return

        salary, ok5 = QInputDialog.getDouble(self.parent, "Αμοιβή", "Εισάγετε την αμοιβή:", 0, 0)
        if not ok5:
            return

        phone, ok6 = QInputDialog.getText(self.parent, "Τηλέφωνο", "Εισάγετε το τηλέφωνο (10 ψηφία):")
        if not ok6 or not (len(phone) == 10 and phone.isdigit()):
            QMessageBox.warning(self.parent, "Σφάλμα", "Το τηλέφωνο πρέπει να αποτελείται από 10 ψηφία.")
            return

        iban, ok7 = QInputDialog.getText(self.parent, "IBAN", "Εισάγετε το IBAN (27 χαρακτήρες, ξεκινά με 'GR'):")
        if not ok7 or not (len(iban) == 27 and iban.startswith('GR')):
            QMessageBox.warning(self.parent, "Σφάλμα", "Το IBAN πρέπει να έχει 27 χαρακτήρες και να ξεκινά με 'GR'.")
            return

        employment, ok8 = QInputDialog.getItem(
            self.parent,
            "Απασχόληση",
            "Επιλέξτε τον τύπο απασχόλησης:",
            ["Γραμματέας", "Προπονητής"],
            0,
            False
        )
        if not ok8:
            return

        # Εισαγωγή δεδομένων στη βάση
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute(f"""
                INSERT INTO {self.table_name} (email, ΑΦΜ, αμοιβή, τηλέφωνο, όνομα, επώνυμο, IBAN)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (email, afm, salary, phone, name, surname, iban))

            if employment == "Προπονητής":
                cursor.execute(f"""INSERT INTO {self.table2_name} (email) VALUES (?)""", (email,))
            elif employment == "Γραμματέας":
                cursor.execute(f"""INSERT INTO {self.table3_name} (email) VALUES (?)""", (email,))

            conn.commit()

            # Ενημέρωση του πίνακα στο UI
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(email))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(surname))
            self.table.setItem(row, 3, QTableWidgetItem(afm))
            self.table.setItem(row, 4, QTableWidgetItem(f"{salary:.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(phone))
            self.table.setItem(row, 6, QTableWidgetItem(iban))
            self.table.setItem(row, 7, QTableWidgetItem(employment))

            delete_button = QPushButton("Διαγραφή")
            update_button = QPushButton("Ενημέρωση")

            delete_button.clicked.connect(lambda checked, row=row: self.delete_member(row))
            update_button.clicked.connect(lambda checked, row=row: self.update_member(row))

            self.table.setCellWidget(row, 8, delete_button)
            self.table.setCellWidget(row, 9, update_button)

            QMessageBox.information(self.parent, "Επιτυχία", "Ο υπάλληλος προστέθηκε επιτυχώς!")
        except sqlite3.IntegrityError as e:
            QMessageBox.warning(self.parent, "Σφάλμα", f"Σφάλμα κατά την εισαγωγή: {e}")
        finally:
            conn.close()
