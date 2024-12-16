import sys
from PyQt6.QtWidgets import QApplication, QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton
from PyQt6.uic import loadUi
import sqlite3
class MyApp(QDialog):
    def __init__(self):
        super().__init__()
        # Φόρτωση του .ui αρχείου
        loadUi("untitled.ui", self)
        self.Buttonstylesheet=self.load_stylesheet("Buttonstyle.txt")
        # Σύνδεση του κουμπιού buttonTableMeli με τη λειτουργία
        self.buttonTableMeli.clicked.connect(self.show_table)

        # Αρχικοποίηση μεταβλητής για παρακολούθηση αν ο πίνακας είναι ήδη ορατός
        self.table_shown = False
        self.table = None

        # Δημιουργία του κουμπιού επιστροφής
        self.backButton = QPushButton("Επιστροφή")
        self.backButton.setStyleSheet(self.Buttonstylesheet)
        self.backButton.clicked.connect(self.go_back)

    def load_stylesheet(self, style):
        try:
            # Ανάγνωση του αρχείου CSS και φόρτωση στο πρόγραμμα
            with open(style, "r") as f:
                stylesheet = f.read()
                print("stylesheet")
                return stylesheet  # Επιστρέφουμε το περιεχόμενο του stylesheet
        except Exception as e:
            print(f"Error loading stylesheet: {e}")
            return None
    def delete_member(self, row):
    # Λήψη του μητρώου του μέλους που θέλουμε να διαγράψουμε
        member_id = self.table.item(row, 0).text()

    # Σύνδεση με τη βάση δεδομένων
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

    # Εκτέλεση του query για τη διαγραφή του μέλους από τη βάση δεδομένων
        cursor.execute("DELETE FROM ΜΕΛΟΣ WHERE μητρώο_μέλους = ?", (member_id,))
        conn.commit()

    # Κλείσιμο της σύνδεσης με τη βάση
        conn.close()

    # Αφαίρεση της διαγραμμένης γραμμής από τον πίνακα
        self.table.removeRow(row) 
    def show_table(self):
        # Αν ο πίνακας υπάρχει ήδη, αφαιρούμε τον
        if self.table_shown:
            self.table.setParent(None)  # Αφαιρούμε τον πίνακα από την καρτέλα
            self.table_shown = False
        else:
            # Δημιουργία του QTableWidget
            self.table = QTableWidget()

            # Σύνδεση με τη βάση δεδομένων
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()

            # Εκτέλεση του query για να πάρουμε τα δεδομένα από τον πίνακα "ΜΕΛΟΣ"
            cursor.execute("SELECT * FROM ΜΕΛΟΣ")
            rows = cursor.fetchall()

            # Κλείσιμο της σύνδεσης με τη βάση
            conn.close()

            # Ρύθμιση του αριθμού των γραμμών και στηλών του πίνακα
            self.table.setRowCount(len(rows))  # Αριθμός γραμμών
            self.table.setColumnCount(9)  # Αριθμός στηλών, μία για κάθε attribute

            # Ετικέτες στηλών
            self.table.setHorizontalHeaderLabels(["Μητρώο Μέλους", "Επώνυμο", "Όνομα", "Ημερομηνία Γέννησης", "Επίπεδο", "Τηλέφωνο","Φύλο" ,"Πλήθος Αδερφών","Διαγραφή"])

            # Προσθήκη δεδομένων στον πίνακα
            for row, row_data in enumerate(rows):
                for column, value in enumerate(row_data):
                    self.table.setItem(row, column, QTableWidgetItem(str(value)))
                delete_button = QPushButton("Διαγραφή")
                delete_button.clicked.connect(lambda state, row=row: self.delete_member(row))
                self.table.setCellWidget(row, 8, delete_button)
            # Εμφάνιση του πίνακα στην καρτέλα "Μέλη"
            tab_index = self.tabWidget.indexOf(self.tabMeli)  # Εντοπισμός της καρτέλας "Μέλη"
            widget = self.tabWidget.widget(tab_index)
            layout = widget.layout()

            # Αν η καρτέλα δεν έχει layout, το προσθέτουμε
            if layout is None:
                layout = QVBoxLayout()
                widget.setLayout(layout)

            # Προσθήκη του πίνακα στο υπάρχον layout της καρτέλας κάτω από το κουμπί
            layout.addWidget(self.table)

            # Προσθήκη του κουμπιού επιστροφής κάτω από τον πίνακα
            layout.addWidget(self.backButton)

            # Σημειώνουμε ότι ο πίνακας εμφανίζεται
            self.table_shown = True
    def go_back(self):
        # Αφαίρεση του πίνακα από το layout και επιστροφή στην αρχική κατάσταση
        if self.table_shown:
            self.table.setParent(None)
            self.table_shown = False

            # Επαναφορά της αρχικής εμφάνισης του κουμπιού
            layout = self.tabWidget.widget(self.tabWidget.indexOf(self.tabMeli)).layout()
            if layout:
                layout.removeWidget(self.backButton)  # Αφαίρεση του κουμπιού επιστροφής
                self.backButton.setParent(None)  # Αφαίρεση του κουμπιού επιστροφής από την οθόνη

            # Επιστροφή στην αρχική κατάσταση του tab
            self.buttonTableMeli.setEnabled(True)  # Ενεργοποιούμε το κουμπί ξανά
            print("Επιστροφή στην αρχική κατάσταση του tab.")
       

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())