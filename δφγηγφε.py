import sys
from PyQt6.QtWidgets import QApplication, QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton
from PyQt6.uic import loadUi
import sqlite3
class MyApp(QDialog):
    def __init__(self):
        super().__init__()
        # Φόρτωση του .ui αρχείου
        loadUi("untitled.ui", self)
 
        # Σύνδεση του κουμπιού buttonTableMeli με τη λειτουργία
        self.buttonTableMeli.clicked.connect(self.show_table)

        # Αρχικοποίηση μεταβλητής για παρακολούθηση αν ο πίνακας είναι ήδη ορατός
        self.table_shown = False
        self.table = None

        # Δημιουργία του κουμπιού επιστροφής
        self.backButton = QPushButton("Επιστροφή")
        self.backButton.setStyleSheet("""
QPushButton {
    font-size: 12px;
    padding: 1px 2.7px;
    font-weight: 500;
    background: #598284;
    color: white;
    border: none;
    position: relative;
    overflow: hidden;
    border-radius: 2px;
    cursor: pointer;
}

QPushButton::hover {
    background: #3f5b5d;
}

QPushButton::pressed {
    transform: scale(0.97);
}

QPushButton .gradient {
    position: absolute;
    width: 100%;
    height: 100%;
    left: 0;
    top: 0;
    border-radius: 2px;
    margin-top: -0.25em;
    background-image: linear-gradient(
        rgba(0, 0, 0, 0),
        rgba(0, 0, 0, 0),
        rgba(0, 0, 0, 0.3)
    );
}

QPushButton .label {
    position: relative;
    top: -1px;
}

QPushButton .transition {
    transition-timing-function: cubic-bezier(0, 0, 0.2, 1);
    transition-duration: 500ms;
    background-color: #3f5b5d;
    border-radius: 9999px;
    width: 0;
    height: 0;
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
}

QPushButton:hover .transition {
    width: 14em;
    height: 14em;
}
""")
        self.backButton.clicked.connect(self.go_back)

    
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
            self.table.setColumnCount(8)  # Αριθμός στηλών, μία για κάθε attribute

            # Ετικέτες στηλών
            self.table.setHorizontalHeaderLabels(["Μητρώο Μέλους", "Επώνυμο", "Όνομα", "Ημερομηνία Γέννησης", "Επίπεδο", "Τηλέφωνο","Φύλο" ,"Πλήθος Αδερφών"])

            # Προσθήκη δεδομένων στον πίνακα
            for row, row_data in enumerate(rows):
                for column, value in enumerate(row_data):
                    self.table.setItem(row, column, QTableWidgetItem(str(value)))

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