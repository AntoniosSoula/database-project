import sys
from PyQt6.QtWidgets import (
    QApplication, QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QPushButton, QMessageBox, QInputDialog, QLineEdit,
)
from PyQt6.uic import loadUi
from functools import partial
import sqlite3


class MyApp(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("untitled.ui", self)
        self.Buttonstylesheet = self.load_stylesheet("Buttonstyle.txt")
        self.buttonTableMeli.clicked.connect(self.show_table)
        self.table_shown = False
        self.table = None
        self.backButton = QPushButton("Επιστροφή")
        self.backButton.setStyleSheet(self.Buttonstylesheet)
        self.backButton.clicked.connect(self.go_back)

        # Κουμπί "Προσθήκη Μέλους" θα εμφανίζεται μόνο στο 'Πίνακας Μελών'
        self.addButton = QPushButton("Προσθήκη Μέλους")
        self.addButton.setStyleSheet(self.Buttonstylesheet)
        self.addButton.clicked.connect(self.add_member)

    def get_next_member_id(self):
        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(μητρώο_μέλους) FROM ΜΕΛΟΣ")
            result = cursor.fetchone()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Σφάλμα Βάσης Δεδομένων", f"Αποτυχία σύνδεσης: {e}")
            return None

        if result[0] is None:
            return "1001"
        last_id = int(result[0])
        next_id = last_id + 1
        return str(next_id).zfill(4)

    def load_stylesheet(self, style):
        try:
            with open(style, "r") as f:
                return f.read()
        except Exception as e:
            QMessageBox.warning(self, "Σφάλμα Φόρτωσης Στυλ", f"Αποτυχία φόρτωσης αρχείου στυλ: {e}")
            return None

    def add_member(self):
        new_member_id = self.get_next_member_id()
        if new_member_id is None:
            return

        try:
            name, ok1 = QInputDialog.getText(self, "Όνομα", "Εισάγετε το όνομα του μέλους:")
            surname, ok2 = QInputDialog.getText(self, "Επώνυμο", "Εισάγετε το επώνυμο του μέλους:")
            if not ok1 or not ok2:
                return

            birth_date, ok3 = QInputDialog.getText(self, "Ημερομηνία Γέννησης",
                                                   "Εισάγετε την ημερομηνία γέννησης (yyyy-MM-dd):")
            level, ok4 = QInputDialog.getItem(self, "Επίπεδο", "Επιλέξτε το επίπεδο του μέλους:",
                                              ["ΑΡΧΑΡΙΟΣ", "ΕΡΑΣΙΤΕΧΝΗΣ", "ΠΡΟΧΩΡΗΜΕΝΟΣ", "ΕΠΑΓΓΕΛΜΑΤΙΑΣ"], 0, False)
            phone, ok5 = QInputDialog.getText(self, "Τηλέφωνο", "Εισάγετε το τηλέφωνο του μέλους:")
            gender, ok6 = QInputDialog.getItem(self, "Φύλο", "Επιλέξτε το φύλο του μέλους:",
                                               ["ΑΡΡΕΝ", "ΘΗΛΥ"], 0, False)
            siblings, ok7 = QInputDialog.getInt(self, "Πλήθος Αδελφών", "Εισάγετε τον αριθμό αδελφών του μέλους:",
                                                0, 0, 10)

            if not (ok1 and ok2 and ok3 and ok4 and ok5 and ok6 and ok7):
                return

            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO ΜΕΛΟΣ (μητρώο_μέλους, όνομα, επώνυμο, ημερομηνία_γέννησης, επίπεδο, τηλέφωνο, φύλο, πλήθος_αδελφών)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                new_member_id,
                name,
                surname,
                birth_date,
                level,
                phone,
                gender,
                siblings
            ))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Επιτυχία", f"Το μέλος με μητρώο {new_member_id} προστέθηκε επιτυχώς.")
        except sqlite3.IntegrityError as e:
            QMessageBox.warning(self, "Σφάλμα", f"Σφάλμα στην προσθήκη μέλους: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Απρόοπτο Σφάλμα", f"Προέκυψε απρόοπτο σφάλμα: {e}")

    def delete_member(self, row):
        try:
            member_id = self.table.item(row, 0).text()
            confirmation = QMessageBox.question(
                self,
                "Επιβεβαίωση Διαγραφής",
                f"Είστε σίγουροι ότι θέλετε να διαγράψετε το μέλος με μητρώο {member_id};",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if confirmation != QMessageBox.StandardButton.Yes:
                return
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ΜΕΛΟΣ WHERE μητρώο_μέλους = ?", (member_id,))
            conn.commit()
            conn.close()
            self.table.removeRow(row)
        except Exception as e:
            QMessageBox.critical(self, "Σφάλμα Διαγραφής", f"Προέκυψε σφάλμα κατά τη διαγραφή: {e}")

    def update_member(self, row):
    # Επιλέγουμε τον αριθμό μητρώου και ζητάμε νέα δεδομένα για ενημέρωση
        member_id = self.table.item(row, 0).text()
        column_names = [
        "Επώνυμο", "Όνομα", "Ημερομηνία Γέννησης", "Επίπεδο", 
        "Τηλέφωνο", "Φύλο", "Πλήθος Αδερφών"
        ]
        column_index = QInputDialog.getInt(
        self, "Επιλογή Πεδίου", "Διάλεξε στήλη για ενημέρωση (1-7):\n" +
        "\n".join([f"{i+1}. {name}" for i, name in enumerate(column_names)]),
        1, 1, len(column_names)
        )[0] - 1  # Γυρίζει σε zero-based index

        if column_index is None:
            return

        new_value, ok = QInputDialog.getText(
            self, "Νέα Τιμή", f"Εισάγετε νέα τιμή για {column_names[column_index]}:")
        if not ok or not new_value:
            return

    # Ελέγχοι για τους περιορισμούς
        if column_index == 2:  # Ημερομηνία Γέννησης
            try:
                QDate.fromString(new_value, "yyyy-MM-dd")
                if QDate.fromString(new_value, "yyyy-MM-dd") > QDate.currentDate():
                    raise ValueError("Η ημερομηνία γέννησης δεν μπορεί να είναι στο μέλλον.")
            except Exception as e:
                QMessageBox.warning(self, "Σφάλμα", f"Μη έγκυρη ημερομηνία γέννησης: {e}")
                return

        elif column_index == 3:  # Επίπεδο
            valid_levels = ['ΑΡΧΑΡΙΟΣ', 'ΕΡΑΣΙΤΕΧΝΗΣ', 'ΠΡΟΧΩΡΗΜΕΝΟΣ', 'ΕΠΑΓΓΕΛΜΑΤΙΑΣ']
            if new_value not in valid_levels:
                QMessageBox.warning(self, "Σφάλμα", "Μη έγκυρο επίπεδο. Πληκτρολογήστε 'ΑΡΧΑΡΙΟΣ' ή 'ΕΡΑΣΙΤΕΧΝΗΣ' ή 'ΠΡΟΧΩΡΗΜΕΝΟΣ' ή 'ΕΠΑΓΓΕΛΜΑΤΙΑΣ'.")
                return

        elif column_index == 4:  # Τηλέφωνο
            if len(new_value) != 10 or not new_value.isdigit():
                QMessageBox.warning(self, "Σφάλμα", "Μη έγκυρο τηλέφωνο. Πρέπει να είναι 10 ψηφία.")
                return

        elif column_index == 5:  # Φύλο
            valid_genders = ['ΑΡΡΕΝ', 'ΘΗΛΥ']
            if new_value not in valid_genders:
                QMessageBox.warning(self, "Σφάλμα", "Μη έγκυρο φύλο. Πληκτρολογήστε 'ΑΡΡΕΝ' ή 'ΘΗΛΥ'.")
                return

        elif column_index == 6:  # Πλήθος Αδερφών
            if not new_value.isdigit() or int(new_value) < 0:
                QMessageBox.warning(self, "Σφάλμα", "Μη έγκυρος αριθμός αδελφών.")
                return

    # Ενημέρωση της βάσης δεδομένων
        columns_db = ["επώνυμο", "όνομα", "ημερομηνία_γέννησης", "επίπεδο", 
                  "τηλέφωνο", "φύλο", "πλήθος_αδελφών"]
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(
        f"UPDATE ΜΕΛΟΣ SET {columns_db[column_index]} = ? WHERE μητρώο_μέλους = ?",
        (new_value, member_id))
        conn.commit()
        conn.close()

    # Ενημέρωση του πίνακα στην εφαρμογή
        self.table.setItem(row, column_index + 1, QTableWidgetItem(new_value))
        print(f"Το μέλος με μητρώο {member_id} ενημερώθηκε.")

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
            self.table.setColumnCount(10)
            self.table.setHorizontalHeaderLabels(
                ["Μητρώο Μέλους", "Επώνυμο", "Όνομα", "Ημερομηνία Γέννησης",
                 "Επίπεδο", "Τηλέφωνο", "Φύλο", "Πλήθος Αδελφών", "Διαγραφή", "Ενημέρωση"]
            )
            for row, row_data in enumerate(rows):
                for column, value in enumerate(row_data):
                    self.table.setItem(row, column, QTableWidgetItem(str(value)))

                delete_button = QPushButton("Διαγραφή")
                delete_button.clicked.connect(partial(self.delete_member, row))
                self.table.setCellWidget(row, 8, delete_button)

                update_button = QPushButton("Ενημέρωση")
                update_button.clicked.connect(partial(self.update_member, row))
                self.table.setCellWidget(row, 9, update_button)

            tab_index = self.tabWidget.indexOf(self.tabMeli)
            widget = self.tabWidget.widget(tab_index)
            layout = widget.layout()
            if layout is None:
                layout = QVBoxLayout()
                widget.setLayout(layout)

            layout.addWidget(self.table)
            layout.addWidget(self.addButton)
            layout.addWidget(self.backButton)
            self.table_shown = True
        

    def go_back(self):
        if self.table_shown:
            self.table.setParent(None)
            self.table_shown = False
            layout = self.tabWidget.widget(self.tabWidget.indexOf(self.tabMeli)).layout()
            if layout:
                layout.removeWidget(self.addButton)
                layout.removeWidget(self.backButton)
                self.addButton.setParent(None)
                self.backButton.setParent(None)
            

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())
