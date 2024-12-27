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
        pass
    def update_member(self):
        pass
