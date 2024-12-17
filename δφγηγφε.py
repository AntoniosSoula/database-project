import sys
from PyQt6.QtWidgets import (
    QApplication, QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout, 
    QPushButton, QMessageBox, QInputDialog, QLineEdit
)
from PyQt6.uic import loadUi
import sqlite3
from functools import partial


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

    def load_stylesheet(self, style):
        try:
            with open(style, "r") as f:
                return f.read()
        except Exception as e:
            print(f"Error loading stylesheet: {e}")
            return None

    def delete_member(self, row):
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
        print(f"Το μέλος με μητρώο {member_id} διαγράφηκε επιτυχώς.")

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
            self, "Νέα Τιμή", f"Εισάγετε νέα τιμή για {column_names[column_index]}:"
        )
        if not ok or not new_value:
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

                # Κουμπί Διαγραφής
                delete_button = QPushButton("Διαγραφή")
                delete_button.clicked.connect(partial(self.delete_member, row))
                self.table.setCellWidget(row, 8, delete_button)

                # Κουμπί Ενημέρωσης
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
            layout.addWidget(self.backButton)
            self.table_shown = True

    def go_back(self):
        if self.table_shown:
            self.table.setParent(None)
            self.table_shown = False
            layout = self.tabWidget.widget(self.tabWidget.indexOf(self.tabMeli)).layout()
            if layout:
                layout.removeWidget(self.backButton)
                self.backButton.setParent(None)
            self.buttonTableMeli.setEnabled(True)
            print("Επιστροφή στην αρχική κατάσταση του tab.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())
