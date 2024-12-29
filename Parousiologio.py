import sqlite3
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QMessageBox, QInputDialog,QComboBox
from PyQt6.QtCore import Qt
from Melos import *
from PyQt6.QtGui import QColor
import re
from Prosopiko import *
from Melos import *
from datetime import datetime
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
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, QPushButton) and widget.text() in ["Προηγούμενη Σελίδα", "Επόμενη Σελίδα", "Προσθήκη Παρουσίας"]:
                layout.takeAt(i).widget().deleteLater()
        layout.addWidget(self.table)

        # Κουμπιά πλοήγησης
        self.add_navigation_buttons(layout)
        self.addButton = QPushButton("Προσθήκη Παρουσίας")
        self.addButton.setStyleSheet(self.Buttonstylesheet)
        self.addButton.clicked.connect(self.add_presence)
        layout.addWidget(self.addButton)

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
            return

        layout.addWidget(combo_box)

        # Κουμπί επιβεβαίωσης
        confirm_button = QPushButton("Επιλογή", dialog)
        layout.addWidget(confirm_button)

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
        member_id, ok2 = QInputDialog.getText(self.parent, "Μητρώο Μέλους", "Εισάγετε Μητρώο Μέλους:")
        if not ok2 or not member_id:
            return
        try:
            cursor.execute(f"""SELECT "{Melos.table_name}"."όνομα", "{Melos.table_name}"."επώνυμο"
                            FROM "{Melos.table_name}" WHERE "{Melos.table_name}"."μητρώο_μέλους" = ?""", (member_id,))
            member_data = cursor.fetchone()
            if not member_data:
                QMessageBox.warning(self.parent, "Σφάλμα", "Το μέλος δεν βρέθηκε.")
                return
            name, surname = member_data
        except sqlite3.Error as e:
            QMessageBox.critical(self.parent, "Σφάλμα", f"Σφάλμα κατά τη φόρτωση Μέλους: {e}")
            return

        date, ok = QInputDialog.getText(self.parent, "Ημερομηνία Παρουσίας", "Εισάγετε την ημερομηνία παρουσίας (YYYY-MM-dd):")
        if not ok or not date:
            QMessageBox.warning(self.parent, "Ακύρωση", "Δεν εισάγατε ημερομηνία παρουσίας.")
            return

        # Έλεγχος μορφής ημερομηνίας
        if not re.match(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$", date):
            QMessageBox.warning(self.parent, "Σφάλμα", "Η ημερομηνία παρουσίας πρέπει να είναι στη μορφή YYYY-MM-dd.")
            return

        try:
            presence_date = datetime.strptime(date, "%Y-%m-%d")
            if presence_date > datetime.now():
                QMessageBox.warning(self.parent, "Σφάλμα", "Η ημερομηνία παρουσίας δεν μπορεί να είναι στο μέλλον.")
                return
        except ValueError:
            QMessageBox.warning(self.parent, "Σφάλμα", "Η ημερομηνία παρουσίας είναι μη έγκυρη.")
            return

        situation, ok8 = QInputDialog.getItem(
            self.parent,
            "Κατάσταση",
            "Επιλέξτε αν ήταν ΠΑΡΩΝ/ΟΥΣΑ ή ΑΠΩΝ/ΟΥΣΑ:",
            ["ΠΑΡΩΝ/ΟΥΣΑ", "ΑΠΩΝ/ΟΥΣΑ"],
            0,
            False
        )
        if not ok8:
            return

        try:
            # Εισαγωγή εγγραφής στη βάση δεδομένων
            cursor.execute(f"""
                INSERT INTO {self.table_name} (email, "μητρώο_μέλους", "κατάσταση", "ημερομηνία προπόνησης")
                VALUES (?, ?, ?, ?)
            """, (email, member_id, situation, date))
            conn.commit()

            # Φόρτωση της νέας εγγραφής από τη βάση
            cursor.execute(f"""
                SELECT "{self.table_name}"."email",
                    "{self.table_name}"."μητρώο_μέλους",
                    "{Melos.table_name}"."όνομα",
                    "{Melos.table_name}"."επώνυμο",
                    "{self.table_name}"."ημερομηνία προπόνησης",
                    "{self.table_name}"."κατάσταση"
                FROM "{self.table_name}"
                JOIN "{Melos.table_name}"
                ON "{Melos.table_name}"."μητρώο_μέλους" = "{self.table_name}"."μητρώο_μέλους"
                WHERE "{self.table_name}"."email" = ? AND "{self.table_name}"."μητρώο_μέλους" = ? 
                AND "{self.table_name}"."ημερομηνία προπόνησης" = ?
            """, (email, member_id, date))
            new_row_data = cursor.fetchone()
            if not new_row_data:
                QMessageBox.warning(self.parent, "Σφάλμα", "Η νέα εγγραφή δεν βρέθηκε για προσθήκη στον πίνακα.")
                return

            # Υπολογισμός της σωστής θέσης εισαγωγής
            all_data_query = f"""
                SELECT "{self.table_name}"."ημερομηνία προπόνησης"
                FROM "{self.table_name}"
                ORDER BY "{self.table_name}"."ημερομηνία προπόνησης" DESC
            """
            cursor.execute(all_data_query)
            all_dates = [datetime.strptime(row[0], "%Y-%m-%d") for row in cursor.fetchall()]
            new_index = all_dates.index(presence_date) if presence_date in all_dates else -1

            if self.current_page * self.rows_per_page <= new_index < (self.current_page + 1) * self.rows_per_page:
                # Αν ανήκει στην τρέχουσα σελίδα, προσθέτουμε
                row_position = new_index % self.rows_per_page
                self.table.insertRow(row_position)

                # Τοποθέτηση δεδομένων στη νέα γραμμή
                for col_idx, value in enumerate(new_row_data):
                    self.table.setItem(row_position, col_idx, QTableWidgetItem(str(value)))

                # Δημιουργία κουμπιού διαγραφής
                delete_button = QPushButton("Διαγραφή")
                delete_button.setStyleSheet(self.Buttonstylesheet)
                delete_button.clicked.connect(lambda checked, row=row_position: self.delete_entry(row))
                self.table.setCellWidget(row_position, 6, delete_button)

            QMessageBox.information(self.parent, "Επιτυχία", "Η παρουσία προστέθηκε επιτυχώς!")
        except sqlite3.IntegrityError as e:
            QMessageBox.warning(self.parent, "Σφάλμα", f"Σφάλμα κατά την εισαγωγή: {e}")
        finally:
            conn.close()
