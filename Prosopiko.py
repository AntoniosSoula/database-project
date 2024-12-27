import sys
from PyQt6.QtWidgets import QApplication, QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QMessageBox,QInputDialog
from PyQt6.uic import loadUi
import sqlite3
from PyQt6.QtCore import QDate


# Κλάση για τη διαχείριση των μελών
class Prosopiko:
    table_name='ΠΡΟΣΩΠΙΚΟ'
    table2_name='ΠΡΟΠΟΝΗΤΗΣ'
    table3_name='ΓΡΑΜΜΑΤΕΑΣ'
    def __init__(self, parent):
        self.parent = parent
        self.table = None
        self.table_shown = False
        self.Buttonstylesheet = self.load_stylesheet("Buttonstyle.txt")
        self.backButton = QPushButton("Επιστροφή")
        self.backButton.setStyleSheet(self.Buttonstylesheet)
        self.backButton.clicked.connect(self.go_back)

    def load_stylesheet(self, style):
        try:
            with open(style, "r") as f:
                return f.read()
        except Exception as e:
            print(f"Error loading stylesheet: {e}")
            return None
    def go_back(self):
        if self.table_shown:
            self.table.setParent(None)
            self.addButton.setParent(None)
            self.backButton.setParent(None)
            self.table_shown = False

            # Καθαρισμός του layout του tabMeli
            layout = self.parent.tabProsopiko.layout()
            if layout is not None:
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

            # Ενεργοποίηση του κουμπιού "Πίνακας Μελών"
            self.parent.buttonTableProsopiko.setEnabled(True)
    def show_table(self):
        if self.table_shown:
            self.table.setParent(None)  # Αφαιρούμε τον πίνακα αν έχει εμφανιστεί ήδη
            self.table_shown = False

        # Δημιουργούμε έναν νέο πίνακα
        self.table = QTableWidget()
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute(f"""SELECT "{self.table_name}"."email", 
                       "{self.table_name}"."όνομα",
                       "{self.table_name}"."επώνυμο",
                       "{self.table_name}"."ΑΦΜ",
                       "{self.table_name}"."αμοιβή",
                       "{self.table_name}"."τηλέφωνο",
                       "{self.table_name}"."IBAN"
                       FROM "{self.table_name}" """)
        rows = cursor.fetchall()
      

        # Ρυθμίσεις του πίνακα
        self.table.setRowCount(len(rows))
        self.table.setColumnCount(10)  # 10 στήλες (συμπεριλαμβανομένων Διαγραφή και Ενημέρωση)
        self.table.setHorizontalHeaderLabels(
            ["Email","Όνομα","Επώνυμο","ΑΦΜ", "Αμοιβή", "Τηλέφωνο", 
            "ΙΒΑΝ", "Απασχόληση", "Διαγραφή", "Ενημέρωση"]
        )

        # Γεμίζουμε τον πίνακα με δεδομένα
        for row, row_data in enumerate(rows):
            for column, value in enumerate(row_data):
                self.table.setItem(row, column, QTableWidgetItem(str(value)))

            email = row_data[0]
            cursor.execute(f"""SELECT COUNT(*) FROM "ΠΡΟΠΟΝΗΤΗΣ" WHERE email = ?""", (email,))
            is_coach = cursor.fetchone()[0] > 0

            cursor.execute(f"""SELECT COUNT(*) FROM "ΓΡΑΜΜΑΤΕΑΣ" WHERE email = ?""", (email,))
            is_secretary = cursor.fetchone()[0] > 0

            employment = "Προπονητής" if is_coach else "Γραμματέας" if is_secretary else "Άγνωστο"
            self.table.setItem(row, 7, QTableWidgetItem(employment))  # Στήλη 7: Απασχόληση
            # Δημιουργία κουμπιού για Διαγραφή και Ενημέρωση για κάθε γραμμή
            delete_button = QPushButton("Διαγραφή")
            update_button = QPushButton("Ενημέρωση")

            # Σύνδεση των κουμπιών με τις αντίστοιχες μεθόδους
            delete_button.clicked.connect(lambda checked, row=row: self.delete_member(row))
            update_button.clicked.connect(lambda checked, row=row: self.update_member(row))

            # Προσθήκη κουμπιών στον πίνακα
            self.table.setCellWidget(row, 8, delete_button)  # Διαγραφή στην στήλη 8
            self.table.setCellWidget(row, 9, update_button)  # Ενημέρωση στην στήλη 9
        conn.close()
        
        layout = self.parent.tabProsopiko.layout()
        if layout is None:
            layout = QVBoxLayout()
            self.parent.tabProsopiko.setLayout(layout)

        layout.addWidget(self.table)
        layout.addWidget(self.backButton)
        self.table_shown = True

        # Δημιουργία και σύνδεση του κουμπιού για προσθήκη νέου μέλους
        self.addButton = QPushButton("Προσθήκη Υπαλλήλου")
        self.addButton.setStyleSheet(self.Buttonstylesheet)
        self.addButton.clicked.connect(self.add_member)
        layout.addWidget(self.addButton)

    def delete_member(self, row):
        item = self.table.item(row, 0)
        if item is None:  # Έλεγχος αν το κελί είναι κενό
            QMessageBox.warning(self.parent, "Σφάλμα", "Δεν βρέθηκε το μητρώο μέλους για διαγραφή.")
            return

        email = item.text()

        # Ερώτημα για επιβεβαίωση διαγραφής
        confirmation = QMessageBox.question(
            self.parent,
            "Επιβεβαίωση Διαγραφής",
            f"Είστε σίγουροι ότι θέλετε να διαγράψετε το μέλος με μητρώο {email};",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirmation != QMessageBox.StandardButton.Yes:
            return

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        try:

            cursor.execute(f"""DELETE FROM "{self.table_name}" WHERE email = ?""", (email,))
            cursor.execute(f"""DELETE FROM "{self.table2_name}" WHERE email = ?""", (email,))
            cursor.execute(f"""DELETE FROM "{self.table3_name}" WHERE email = ?""", (email,))

            # Επιβεβαίωση και αποθήκευση των αλλαγών στη βάση δεδομένων
            conn.commit()
            QMessageBox.information(self.parent, "Επιτυχία", f"Το μέλος με μητρώο {email} διαγράφηκε επιτυχώς.")
            
            # Διαγραφή από τον πίνακα στο UI
            self.table.removeRow(row)
            print(f"Το μέλος με μητρώο {email} διαγράφηκε επιτυχώς.")

        except sqlite3.Error as e:
            # Σε περίπτωση σφάλματος κατά τη διαγραφή από τη βάση
            conn.rollback()  # Αν κάτι πάει στραβά, αναιρούμε τις αλλαγές
            QMessageBox.warning(self.parent, "Σφάλμα", f"Σφάλμα κατά τη διαγραφή του μέλους: {e}")
        
        finally:
            # Κλείσιμο της σύνδεσης με τη βάση
            conn.close()
    def add_member(self):
        # Λήψη δεδομένων για νέο υπάλληλο
        email, ok1 = QInputDialog.getText(self.parent, "Email", "Εισάγετε το email του υπαλλήλου:")
        if not ok1 or not email:
            return

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
            
            # Ανάλογα με τον τύπο απασχόλησης, εισάγουμε στο σωστό table
            if employment == "Προπονητής":
                cursor.execute(f"""INSERT INTO {self.table2_name} (email) VALUES (?)""", (email,))
            elif employment == "Γραμματέας":
                cursor.execute(f"""INSERT INTO {self.table3_name} (email) VALUES (?)""", (email,))
            
            conn.commit()

            # Ενημέρωση του UI πίνακα
            row = self.table.rowCount()  # Λήψη του τρέχοντος αριθμού γραμμών
            self.table.insertRow(row)  # Προσθήκη νέας γραμμής

            # Ρύθμιση των κελιών με τα νέα δεδομένα
            self.table.setItem(row, 0, QTableWidgetItem(email))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(surname))
            self.table.setItem(row, 3, QTableWidgetItem(afm))
            self.table.setItem(row, 4, QTableWidgetItem(f"{salary:.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(phone))
            self.table.setItem(row, 6, QTableWidgetItem(iban))
            self.table.setItem(row, 7, QTableWidgetItem(employment))  # Προσθήκη απασχόλησης

            # Δημιουργία κουμπιών Διαγραφή και Ενημέρωση
            delete_button = QPushButton("Διαγραφή")
            update_button = QPushButton("Ενημέρωση")

            # Σύνδεση κουμπιών με τις αντίστοιχες μεθόδους
            delete_button.clicked.connect(lambda checked, row=row: self.delete_member(row))
            update_button.clicked.connect(lambda checked, row=row: self.update_member(row))

            # Προσθήκη κουμπιών στον πίνακα
            self.table.setCellWidget(row, 8, delete_button)  # Διαγραφή στην στήλη 8
            self.table.setCellWidget(row, 9, update_button)  # Ενημέρωση στην στήλη 9

            QMessageBox.information(self.parent, "Επιτυχία", "Ο υπάλληλος προστέθηκε επιτυχώς!")
        except sqlite3.IntegrityError as e:
            QMessageBox.warning(self.parent, "Σφάλμα", f"Σφάλμα κατά την εισαγωγή: {e}")
        finally:
            conn.close()

    def update_member(self, row):
            # Επιλέγουμε το email και ζητάμε νέα δεδομένα για ενημέρωση
            email = self.table.item(row, 0).text()  # Το email είναι στην πρώτη στήλη του πίνακα

            column_names = [
                "Όνομα", "Επώνυμο", "ΑΦΜ", "Αμοιβή", "Τηλέφωνο", "IBAN"
            ]

            # Περνάμε την parent (QDialog) ως το πρώτο όρισμα
            column_index, ok = QInputDialog.getInt(
                self.parent,  # parent πρέπει να είναι το QDialog (δηλαδή self.parent)
                "Επιλογή Πεδίου", 
                "Διάλεξε στήλη για ενημέρωση (1-6):\n" + "\n".join([f"{i+1}. {name}" for i, name in enumerate(column_names)]),
                1, 1, len(column_names)
            )

            if not ok:
                return

            column_index -= 1  # Γυρίζει σε zero-based index

            if column_index is None:
                return

            new_value, ok = QInputDialog.getText(
                self.parent, "Νέα Τιμή", f"Εισάγετε νέα τιμή για {column_names[column_index]}:"
            )
            if not ok or not new_value:
                return

            # Ελέγχοι για τους περιορισμούς
            if column_index == 2:  # ΑΦΜ
                if len(new_value) != 9 or not new_value.isdigit():
                    QMessageBox.warning(self.parent, "Σφάλμα", "Μη έγκυρο ΑΦΜ. Πρέπει να έχει 9 ψηφία.")
                    return

            elif column_index == 3:  # Αμοιβή
                try:
                    float(new_value)  # Έλεγχος αν η αμοιβή είναι αριθμός
                    if float(new_value) < 0:
                        QMessageBox.warning(self.parent, "Σφάλμα", "Η αμοιβή πρέπει να είναι θετικός αριθμός.")
                        return
                except ValueError:
                    QMessageBox.warning(self.parent, "Σφάλμα", "Η αμοιβή πρέπει να είναι αριθμός.")
                    return

            elif column_index == 4:  # Τηλέφωνο
                if len(new_value) != 10 or not new_value.isdigit():
                    QMessageBox.warning(self.parent, "Σφάλμα", "Μη έγκυρο τηλέφωνο. Πρέπει να είναι 10 ψηφία.")
                    return

            elif column_index == 5:  # IBAN
                if len(new_value) != 27 or not new_value.startswith('GR'):
                    QMessageBox.warning(self.parent, "Σφάλμα", "Μη έγκυρο IBAN. Πρέπει να έχει 27 χαρακτήρες και να ξεκινάει με 'GR'.")
                    return

            # Ενημέρωση της βάσης δεδομένων
            columns_db = ["όνομα", "επώνυμο", "ΑΦΜ", "αμοιβή", "τηλέφωνο", "IBAN"]
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            try:
                cursor.execute(
                    f"""UPDATE {self.table_name} SET {columns_db[column_index]} = ? WHERE email = ?""",
                    (new_value, email)
                )
                conn.commit()

                # Ενημέρωση του πίνακα στην εφαρμογή
                self.table.setItem(row, column_index + 1, QTableWidgetItem(new_value))
                QMessageBox.information(self.parent, "Επιτυχία", f"Τα δεδομένα για το email {email} ενημερώθηκαν επιτυχώς.")
            except sqlite3.Error as e:
                QMessageBox.critical(self.parent, "Σφάλμα", f"Σφάλμα κατά την ενημέρωση της βάσης: {e}")
            finally:
                conn.close()
