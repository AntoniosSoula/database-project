import sys
from PyQt6.QtWidgets import QApplication, QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QMessageBox,QInputDialog
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
                
                # Δημιουργία κουμπιού για Διαγραφή και Ενημέρωση για κάθε γραμμή
                delete_button = QPushButton("Διαγραφή")
                update_button = QPushButton("Ενημέρωση")

                # Σύνδεση των κουμπιών με τις αντίστοιχες μεθόδους
                delete_button.clicked.connect(lambda checked, row=row: self.delete_member(row))
                update_button.clicked.connect(lambda checked, row=row: self.update_member(row))

                self.table.setCellWidget(row, 8, delete_button)  # Διαγραφή στην στήλη 8
                self.table.setCellWidget(row, 9, update_button)  # Ενημέρωση στην στήλη 9

            # Προσθήκη του πίνακα στο tabMeli
            layout = self.parent.tabMeli.layout() if self.parent.tabMeli.layout() else QVBoxLayout()
            self.parent.tabMeli.setLayout(layout)
            layout.addWidget(self.table)

            self.table_shown = True


    def delete_member(self, row):
        item = self.table.item(row, 0)
        if item is None:  # Έλεγχος αν το κελί είναι κενό
            QMessageBox.warning(self.parent, "Σφάλμα", "Δεν βρέθηκε το μητρώο μέλους για διαγραφή.")
            return

        member_id = item.text()
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
        cursor.execute("DELETE FROM ΜΕΛΟΣ WHERE μητρώο_μέλους = ?", (member_id,))
        conn.commit()
        conn.close()
        self.table.removeRow(row)
        print(f"Το μέλος με μητρώο {member_id} διαγράφηκε επιτυχώς.")

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
            f"UPDATE ΜΕΛΟΣ SET {columns_db[column_index]} = ? WHERE μητρώο_μέλους = ?",
            (new_value, member_id)
        )
        conn.commit()
        conn.close()

        # Ενημέρωση του πίνακα στην εφαρμογή
        self.table.setItem(row, column_index + 1, QTableWidgetItem(new_value))
        print(f"Το μέλος με μητρώο {member_id} ενημερώθηκε.")

    def get_next_member_id(self):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(μητρώο_μέλους) FROM ΜΕΛΟΣ")
        result = cursor.fetchone()
        conn.close()

        # Αν δεν υπάρχουν μέλη, ξεκινάμε από το 1001
        if result[0] is None:
            return "0001"

        # Εξάγουμε το τελευταίο μητρώο και το αυξάνουμε κατά 1
        last_id = int(result[0])
        next_id = last_id + 1
        return str(next_id).zfill(4)  # Επιστρέφουμε το επόμενο μητρώο με 4 ψηφία

class Main(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("untitled.ui", self)
        self.melos = None  # Αρχικοποιούμε το στιγμιότυπο της κλάσης Meli

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
