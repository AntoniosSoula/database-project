import sys
from PyQt6.QtWidgets import QTableWidgetItem, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QMessageBox,QInputDialog,QLineEdit
from PyQt6.uic import loadUi
import sqlite3
from PyQt6.QtCore import QDate
from PyQt6.QtCore import Qt

# Κλάση για τη διαχείριση των μελών
class Melos:
    table_name='ΜΕΛΟΣ'
    def __init__(self, parent):
        self.parent = parent
        self.table = None
        self.table_shown = False
        self.Buttonstylesheet = self.load_stylesheet("Buttonstyle.txt")
        self.backButton = QPushButton("Επιστροφή")
        self.backButton.setStyleSheet(self.Buttonstylesheet)
        self.backButton.clicked.connect(self.go_back)

        if not hasattr(self, 'searchBar') or self.searchBar is None:
            self.searchBar = QLineEdit()
            self.searchBar.setPlaceholderText("Αναζήτηση...")
            self.searchBar.textChanged.connect(self.search_member)
    def load_stylesheet(self, style):
        try:
            with open(style, "r") as f:
                return f.read()
        except Exception as e:
            print(f"Error loading stylesheet: {e}")
            return None
    def show_table(self):
        if self.table_shown:
            self.table.setParent(None)  # Αφαιρούμε τον πίνακα αν έχει εμφανιστεί ήδη
            self.table_shown = False


        # Δημιουργούμε έναν νέο πίνακα
        self.table = QTableWidget()
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute(f"SELECT * FROM {self.table_name}")
        rows = cursor.fetchall()
        conn.close()

        # Ρυθμίσεις του πίνακα
        self.table.setRowCount(len(rows))
        self.table.setColumnCount(10)  # 10 στήλες (συμπεριλαμβανομένων Διαγραφή και Ενημέρωση)
        self.table.setHorizontalHeaderLabels(
            ["Μητρώο Μέλους", "Επώνυμο", "Όνομα", "Ημερομηνία Γέννησης", 
            "Επίπεδο", "Τηλέφωνο", "Φύλο", "Πλήθος Αδερφών", "Διαγραφή", "Ενημέρωση"]
        )

        # Γεμίζουμε τον πίνακα με δεδομένα
        for row, row_data in enumerate(rows):
            for column, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)  # Μη επεξεργάσιμο στοιχείο
                self.table.setItem(row, column, item)
            # Δημιουργία κουμπιού για Διαγραφή και Ενημέρωση για κάθε γραμμή
            delete_button = QPushButton("Διαγραφή")
            update_button = QPushButton("Ενημέρωση")
            delete_button.setStyleSheet(self.Buttonstylesheet)
            update_button.setStyleSheet(self.Buttonstylesheet)
            # Σύνδεση των κουμπιών με τις αντίστοιχες μεθόδους
            delete_button.clicked.connect(lambda checked, row=row: self.delete_member(row))
            update_button.clicked.connect(lambda checked, row=row: self.update_member(row))

            # Προσθήκη κουμπιών στον πίνακα
            self.table.setCellWidget(row, 8, delete_button)  # Διαγραφή στην στήλη 8
            self.table.setCellWidget(row, 9, update_button)  # Ενημέρωση στην στήλη 9

        # Προσθήκη του πίνακα στο tabMeli μόνο αν δεν έχει ήδη προστεθεί
        layout = self.parent.tabMeli.layout()
        if layout is None:
            layout = QVBoxLayout()
            self.parent.tabMeli.setLayout(layout)
        if not hasattr(self, "searchBar_added") or not self.searchBar_added:
            layout.addWidget(self.searchBar)
            self.searchBar_added = True
 
        layout.addWidget(self.table)
        layout.addWidget(self.backButton)
        self.table_shown = True

        # Δημιουργία και σύνδεση του κουμπιού για προσθήκη νέου μέλους
        self.addButton = QPushButton("Προσθήκη Μέλους")
        self.addButton.setStyleSheet(self.Buttonstylesheet)
        self.addButton.clicked.connect(self.add_member)
        layout.addWidget(self.addButton)
    
    def add_member(self):
        # Λήψη του επόμενου μητρώου
        new_member_id = self.get_next_member_id()

        # Αναζήτηση στοιχείων του μέλους από τον χρήστη
        name, ok1 = QInputDialog.getText(self.parent, "Όνομα", "Εισάγετε το όνομα του μέλους:")  # Use self.parent here
        surname, ok2 = QInputDialog.getText(self.parent, "Επώνυμο", "Εισάγετε το επώνυμο του μέλους:")  # Use self.parent here

        if not ok1 or not ok2:  # Αν δεν επιβεβαιώσει τα δεδομένα, επιστρέφουμε
            return

        birth_date, ok3 = QInputDialog.getText(self.parent, "Ημερομηνία Γέννησης", "Εισάγετε την ημερομηνία γέννησης (yyyy-MM-dd):")  # Use self.parent here
        level, ok4 = QInputDialog.getItem(self.parent, "Επίπεδο", "Επιλέξτε το επίπεδο του μέλους:", ["ΑΡΧΑΡΙΟΣ", "ΕΡΑΣΙΤΕΧΝΗΣ", "ΠΡΟΧΩΡΗΜΕΝΟΣ", "ΕΠΑΓΓΕΛΜΑΤΙΑΣ"], 0, False)  # Use self.parent here
        phone, ok5 = QInputDialog.getText(self.parent, "Τηλέφωνο", "Εισάγετε το τηλέφωνο του μέλους:")  # Use self.parent here
        gender, ok6 = QInputDialog.getItem(self.parent, "Φύλο", "Επιλέξτε το φύλο του μέλους:", ["ΑΡΡΕΝ", "ΘΗΛΥ"], 0, False)  # Use self.parent here
        siblings, ok7 = QInputDialog.getInt(self.parent, "Πλήθος Αδελφών", "Εισάγετε τον αριθμό αδελφών του μέλους:", 0, 0, 10)  # Use self.parent here

        if not (ok1 and ok2 and ok3 and ok4 and ok5 and ok6 and ok7):
            return  # Αν κάποιος από τους χρήστες δεν έχει εισάγει τα δεδομένα ή ακύρωσε, επιστρέφουμε

        # Ανοίγουμε τη σύνδεση στη βάση δεδομένων και εισάγουμε τα δεδομένα
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute(f"""
                INSERT INTO {self.table_name} (μητρώο_μέλους, όνομα, επώνυμο, ημερομηνία_γέννησης, επίπεδο, τηλέφωνο, φύλο, πλήθος_αδελφών)
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

            # Εμφάνιση μηνύματος επιτυχίας
            QMessageBox.information(self.parent, "Επιτυχία", f"Το μέλος με μητρώο {new_member_id} προστέθηκε επιτυχώς.")
            row = self.table.rowCount()  # Λήψη του τρέχοντος αριθμού γραμμών
            self.table.insertRow(row)  # Προσθήκη νέας γραμμής

            # Ρύθμιση των κελιών με τα νέα δεδομένα
            self.table.setItem(row, 0, QTableWidgetItem(new_member_id))
            self.table.setItem(row, 1, QTableWidgetItem(surname))
            self.table.setItem(row, 2, QTableWidgetItem(name))
            self.table.setItem(row, 3, QTableWidgetItem(birth_date))
            self.table.setItem(row, 4, QTableWidgetItem(level))
            self.table.setItem(row, 5, QTableWidgetItem(phone))
            self.table.setItem(row, 6, QTableWidgetItem(gender))
            self.table.setItem(row, 7, QTableWidgetItem(str(siblings)))
            
            delete_button = QPushButton("Διαγραφή")
            update_button = QPushButton("Ενημέρωση")

            # Σύνδεση κουμπιών με τις αντίστοιχες μεθόδους
            delete_button.clicked.connect(lambda checked, row=row: self.delete_member(row))
            update_button.clicked.connect(lambda checked, row=row: self.update_member(row))

            self.table.setCellWidget(row, 8, delete_button)  # Διαγραφή στην στήλη 8
            self.table.setCellWidget(row, 9, update_button)  # Ενημέρωση στην στήλη 9
        except sqlite3.IntegrityError as e:
            print(f"Σφάλμα κατά την εισαγωγή στην βάση: {e}")
            QMessageBox.warning(self.parent, "Σφάλμα", f"Σφάλμα στην προσθήκη μέλους: {e}")

    def delete_member(self, row):
        item = self.table.item(row, 0)
        if item is None:  # Έλεγχος αν το κελί είναι κενό
            QMessageBox.warning(self.parent, "Σφάλμα", "Δεν βρέθηκε το μητρώο μέλους για διαγραφή.")
            return

        member_id = item.text()

        # Ερώτημα για επιβεβαίωση διαγραφής
        confirmation = QMessageBox.question(
            self.parent,
            "Επιβεβαίωση Διαγραφής",
            f"Είστε σίγουροι ότι θέλετε να διαγράψετε το μέλος με μητρώο {member_id};",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirmation != QMessageBox.StandardButton.Yes:
            return

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        try:

            cursor.execute(f"DELETE FROM {self.table_name} WHERE μητρώο_μέλους = ?", (member_id,))
            
            cursor.execute(f"DELETE FROM 'ΠΑΙΚΤΗΣ' WHERE μητρώο_μέλους = ?", (member_id,))

            # Διαγραφή από τον πίνακα "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ"
            cursor.execute(f"DELETE FROM 'ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ' WHERE μητρώο_μέλους = ?", (member_id,))

            # Διαγραφή από τον πίνακα "ΞΕΝΟΣ ΠΑΙΚΤΗΣ"
            cursor.execute(f"DELETE FROM 'ΞΕΝΟΣ ΠΑΙΚΤΗΣ' WHERE μητρώο_μέλους = ?", (member_id,))

            # Επιβεβαίωση και αποθήκευση των αλλαγών στη βάση δεδομένων
            conn.commit()
            QMessageBox.information(self.parent, "Επιτυχία", f"Το μέλος με μητρώο {member_id} διαγράφηκε επιτυχώς.")
            
            # Διαγραφή από τον πίνακα στο UI
            self.table.removeRow(row)
            print(f"Το μέλος με μητρώο {member_id} διαγράφηκε επιτυχώς.")

        except sqlite3.Error as e:
            # Σε περίπτωση σφάλματος κατά τη διαγραφή από τη βάση
            conn.rollback()  # Αν κάτι πάει στραβά, αναιρούμε τις αλλαγές
            QMessageBox.warning(self.parent, "Σφάλμα", f"Σφάλμα κατά τη διαγραφή του μέλους: {e}")
        
        finally:
            # Κλείσιμο της σύνδεσης με τη βάση
            conn.close()

    def update_member(self, row):
        # Επιλέγουμε τον αριθμό μητρώου και ζητάμε νέα δεδομένα για ενημέρωση
        member_id = self.table.item(row, 0).text()
        column_names = [
            "Επώνυμο", "Όνομα", "Ημερομηνία Γέννησης", "Επίπεδο", 
            "Τηλέφωνο", "Φύλο", "Πλήθος Αδερφών"
        ]
        
        # Περνάμε την parent (QDialog) ως το πρώτο όρισμα
        column_index, ok = QInputDialog.getInt(
            self.parent,  # parent πρέπει να είναι το QDialog (δηλαδή self.parent)
            "Επιλογή Πεδίου", 
            "Διάλεξε στήλη για ενημέρωση (1-7):\n" + "\n".join([f"{i+1}. {name}" for i, name in enumerate(column_names)]),
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
        if column_index == 2:  # Ημερομηνία Γέννησης
            try:
                QDate.fromString(new_value, "yyyy-MM-dd")
                if QDate.fromString(new_value, "yyyy-MM-dd") > QDate.currentDate():
                    raise ValueError("Η ημερομηνία γέννησης δεν μπορεί να είναι στο μέλλον.")
            except Exception as e:
                QMessageBox.warning(self.parent, "Σφάλμα", f"Μη έγκυρη ημερομηνία γέννησης: {e}")
                return

        elif column_index == 3:  # Επίπεδο
            valid_levels = ['ΑΡΧΑΡΙΟΣ', 'ΕΡΑΣΙΤΕΧΝΗΣ', 'ΠΡΟΧΩΡΗΜΕΝΟΣ', 'ΕΠΑΓΓΕΛΜΑΤΙΑΣ']
            if new_value not in valid_levels:
                QMessageBox.warning(self.parent, "Σφάλμα", "Μη έγκυρο επίπεδο. Πληκτρολογήστε 'ΑΡΧΑΡΙΟΣ' ή 'ΕΡΑΣΙΤΕΧΝΗΣ' ή 'ΠΡΟΧΩΡΗΜΕΝΟΣ' ή 'ΕΠΑΓΓΕΛΜΑΤΙΑΣ'.")
                return

        elif column_index == 4:  # Τηλέφωνο
            if len(new_value) != 10 or not new_value.isdigit():
                QMessageBox.warning(self.parent, "Σφάλμα", "Μη έγκυρο τηλέφωνο. Πρέπει να είναι 10 ψηφία.")
                return

        elif column_index == 5:  # Φύλο
            valid_genders = ['ΑΡΡΕΝ', 'ΘΗΛΥ']
            if new_value not in valid_genders:
                QMessageBox.warning(self.parent, "Σφάλμα", "Μη έγκυρο φύλο. Πληκτρολογήστε 'ΑΡΡΕΝ' ή 'ΘΗΛΥ'.")
                return

        elif column_index == 6:  # Πλήθος Αδερφών
            if not new_value.isdigit() or int(new_value) < 0:
                QMessageBox.warning(self.parent, "Σφάλμα", "Μη έγκυρος αριθμός αδελφών.")
                return

        # Ενημέρωση της βάσης δεδομένων
        columns_db = ["επώνυμο", "όνομα", "ημερομηνία_γέννησης", "επίπεδο", 
                    "τηλέφωνο", "φύλο", "πλήθος_αδελφών"]
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE {self.table_name} SET {columns_db[column_index]} = ? WHERE μητρώο_μέλους = ?",
            (new_value, member_id)
        )
        conn.commit()
        conn.close()
                
        item = QTableWidgetItem(new_value)
        item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        self.table.setItem(row, column_index + 1, item)
        print(f"Το μέλος με μητρώο {member_id} ενημερώθηκε.")

    def get_next_member_id(self):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT MAX(μητρώο_μέλους) FROM {self.table_name}")
        result = cursor.fetchone()
        conn.close()

        # Αν δεν υπάρχουν μέλη, ξεκινάμε από το 1001
        if result[0] is None:
            return "0001"

        # Εξάγουμε το τελευταίο μητρώο και το αυξάνουμε κατά 1
        last_id = int(result[0])
        next_id = last_id + 1
        return str(next_id).zfill(4)  # Επιστρέφουμε το επόμενο μητρώο με 4 ψηφία
    def go_back(self):
        if self.table_shown:
            self.table.setParent(None)
            self.addButton.setParent(None)
            self.backButton.setParent(None)
            self.table_shown = False

            # Καθαρισμός του layout του tabMeli
            layout = self.parent.tabMeli.layout()
            if layout is not None:
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

            # Ενεργοποίηση του κουμπιού "Πίνακας Μελών"
            self.parent.buttonTableMeli.setEnabled(True)
    def search_member(self):
        
        search_text = self.searchBar.text()

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE μητρώο_μέλους LIKE ? OR
                  επώνυμο LIKE ? OR
                  όνομα LIKE ? OR
                  "ημρομηνία γέννησης" LIKE ?  OR
                  "τηλέφωνο" LIKE ? OR
                  "φύλο" LIKE ?
        """

        cursor.execute(query, (f"%{search_text}%", f"%{search_text}%", f"%{search_text}%",f"%{search_text}%", f"%{search_text}%", f"%{search_text}%"))
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))

        for row in range(len(rows)):
            for column, value in enumerate(rows[row]):
                item = QTableWidgetItem(str(value))
                item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)  # Μη επεξεργάσιμο στοιχείο
                self.table.setItem(row, column, item)
        if self.table.cellWidget(row, 8):
            self.table.cellWidget(row, 8).deleteLater()
        if self.table.cellWidget(row, 9):
            self.table.cellWidget(row, 9).deleteLater()
            delete_button = QPushButton("Διαγραφή")
            update_button = QPushButton("Ενημέρωση")
            delete_button.setStyleSheet(self.Buttonstylesheet)
            update_button.setStyleSheet(self.Buttonstylesheet)

            delete_button.clicked.connect(lambda checked, row=row: self.delete_member(row))
            update_button.clicked.connect(lambda checked, row=row: self.update_member(row))

            self.table.setCellWidget(row, 8, delete_button)
            self.table.setCellWidget(row, 9, update_button)