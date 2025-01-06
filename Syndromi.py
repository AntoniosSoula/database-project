# Syndromi.py
import sqlite3
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QMessageBox, QInputDialog
from PyQt6.QtCore import Qt
from Melos import *
from PyQt6.QtGui import QColor
import re
from datetime import datetime
class Syndromi:
    table_name = 'ΣΥΝΔΡΟΜΗ'  # Ή το σωστό όνομα πίνακα για τους συνδρομητές

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
    def show_table(self):
        if self.table_shown:
            self.table.setParent(None)  # Αφαιρούμε τον πίνακα αν έχει εμφανιστεί ήδη
            self.table_shown = False
            
        self.table = QTableWidget()
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {self.table_name}")
        rows = cursor.fetchall()
        conn.close()

        # Αν δεν υπάρχουν δεδομένα, δείχνουμε μήνυμα
        if not rows:
            QMessageBox.warning(self.parent, "Προσοχή", "Δεν υπάρχουν συνδρομητές.")
            return

        # Ρύθμιση του πίνακα
        self.table.setRowCount(len(rows))
        self.table.setColumnCount(len(rows[0]))  # Ο αριθμός των στηλών είναι το μέγεθος της πρώτης γραμμής
        self.table.setHorizontalHeaderLabels(["ID", "Όνομα", "Ημερομηνία Εγγραφής", "Άλλες Στήλες"])  # Εξαρτάται από τις στήλες της βάσης δεδομένων

        # Προσθήκη των δεδομένων στον πίνακα
        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))


        layout = self.parent.tabSyndromi.layout()
        if layout is None:
            layout = QVBoxLayout()
            self.parent.tabSyndromi.setLayout(layout)

        layout.addWidget(self.table)
        layout.addWidget(self.backButton)
        self.table_shown = True


    def go_back(self):
        if self.table_shown:
            self.table.setParent(None)
            self.backButton.setParent(None)
            self.table_shown = False

            # Καθαρισμός του layout του tabMeli
            layout = self.parent.tabSyndromi.layout()
            if layout is not None:
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

            # Ενεργοποίηση του κουμπιού "Πίνακας Μελών"
            self.parent.buttonSyndromh.setEnabled(True)
            self.parent.buttonEE.setEnabled(True)          
            self.parent.buttonPliromon.setEnabled(True)  

class MelosPlironeiSyndromi(Syndromi,Melos):
    table_name='ΜΕΛΟΣ_ΠΛΗΡΩΝΕΙ_ΣΥΝΔΡΟΜΗ'
    def __init__(self,parent):
        Syndromi.__init__(self,parent)
        Melos.__init__(self,parent)
    
    def go_back(self):
        if self.table_shown:
            self.table.setParent(None)
            self.backButton.setParent(None)
            self.table_shown = False

            # Καθαρισμός του layout του tabMeli
            layout = self.parent.tabSyndromi.layout()
            if layout is not None:
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()

            # Ενεργοποίηση του κουμπιού "Πίνακας Μελών"
            self.parent.buttonPliromon.setEnabled(True)
            self.parent.buttonSyndromh.setEnabled(True)
            self.parent.buttonEE.setEnabled(True)   
    def show_table(self):
        query = (f"""SELECT "{Melos.table_name}"."μητρώο_μέλους",
        "{Melos.table_name}"."όνομα",
        "{Melos.table_name}"."επώνυμο",
        "{Syndromi.table_name}"."τρόπος πληρωμής",
        "{Syndromi.table_name}"."πακέτο συνδρομής",20*(
        0.8*("{self.table_name}"."κωδικός συνδρομής"=1 OR "{self.table_name}"."κωδικός συνδρομής"=6) +
        0.7*("{self.table_name}"."κωδικός συνδρομής"=2 OR "{self.table_name}"."κωδικός συνδρομής"=7) +
        1.1*("{self.table_name}"."κωδικός συνδρομής"=3 OR "{self.table_name}"."κωδικός συνδρομής"=8) +
        0.6*("{self.table_name}"."κωδικός συνδρομής"=4 OR "{self.table_name}"."κωδικός συνδρομής"=9) +
        1*("{self.table_name}"."κωδικός συνδρομής"=5 OR "{self.table_name}"."κωδικός συνδρομής"=10))
        AS "ποσό",
        "{self.table_name}"."ημερομηνία πληρωμής"
    FROM 
        "{self.table_name}"
    JOIN 
        "{Melos.table_name}"
    ON 
        "{Melos.table_name}"."μητρώο_μέλους" = "{self.table_name}"."μητρώο_μέλους"
    JOIN 
        "{Syndromi.table_name}"
    ON 
        "{Syndromi.table_name}"."κωδικός συνδρομής" = "{self.table_name}"."κωδικός συνδρομής"
    ORDER BY 
        CAST(SUBSTR("{self.table_name}"."ημερομηνία πληρωμής", 4, 4) AS INTEGER) DESC,
        CAST(SUBSTR("{self.table_name}"."ημερομηνία πληρωμής", 1, 2) AS INTEGER) DESC   
""")

        if self.table_shown:
            self.table.setParent(None)  # Αφαιρούμε τον πίνακα αν έχει εμφανιστεί ήδη
            self.table_shown = False

    # Δημιουργούμε έναν νέο πίνακα
        self.table = QTableWidget()
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        # Ρυθμίσεις του πίνακα
        self.table.setRowCount(len(rows))
        self.table.setColumnCount(8)  # 7 στήλες (συμπεριλαμβανομένων Διαγραφή και Ενημέρωση)
        self.table.setHorizontalHeaderLabels([
            "Μητρώο Μέλους", "Όνομα", "Επώνυμο", "Τρόπος Πληρωμής",
            "Πακέτο Συνδρομής", "Ποσό", "Ημερομηνία Πληρωμής", "Διαγραφή"]
        )

        # Γεμίζουμε τον πίνακα με δεδομένα
        for row, row_data in enumerate(rows):
            for column, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)  # Μη επεξεργάσιμο στοιχείο
                self.table.setItem(row, column, item)

            # Δημιουργία κουμπιού για Διαγραφή
            delete_button = QPushButton("Διαγραφή")
            delete_button.setStyleSheet(self.Buttonstylesheet)
            delete_button.clicked.connect(lambda checked, row=row: self.delete_entry(row))
            self.table.setCellWidget(row, 7, delete_button)  


        layout = self.parent.tabSyndromi.layout()
        if layout is None:
            layout = QVBoxLayout()
            self.parent.tabSyndromi.setLayout(layout)
        self.search_bar = QLineEdit()  # Νέο αντικείμενο QLineEdit κάθε φορά
        self.search_bar.setPlaceholderText("Αναζήτηση...")
        self.search_bar.textChanged.connect(self.search_member)  # Συνδέουμε το νέο αντικείμενο

            # Προσθήκη widgets στο layout
        layout.addWidget(self.search_bar)
        layout.addWidget(self.table)
        layout.addWidget(self.backButton)
        self.table_shown = True

        # Δημιουργία και σύνδεση του  για προσθήκη νέας εγγραφής
        self.addButton = QPushButton("Προσθήκη Πληρωμής")
        self.addButton.setStyleSheet(self.Buttonstylesheet)
        self.addButton.clicked.connect(self.add_payment)
        layout.addWidget(self.addButton)
        self.debtsButton = QPushButton("Πίνακας Οφειλών")
        self.debtsButton.setStyleSheet(self.Buttonstylesheet)
        self.debtsButton.clicked.connect(self.show_debts_table)
        layout.addWidget(self.debtsButton)

    def delete_entry(self, row):
        item = self.table.item(row, 0)
        if item is None:  # Έλεγχος αν το κελί είναι κενό
            QMessageBox.warning(self.parent, "Σφάλμα", "Δεν βρέθηκε το στοιχείο για διαγραφή.")
            return

        member_id = item.text()
        date_item = self.table.item(row, 6)
        payment_method_item = self.table.item(row, 3)
        subscription_package_item = self.table.item(row, 4)

        if payment_method_item is None or subscription_package_item is None:
            QMessageBox.warning(self.parent, "Σφάλμα", "Δεν βρέθηκαν τα στοιχεία τρόπου πληρωμής ή πακέτου συνδρομής.")
            return
        if date_item is None:
            QMessageBox.warning(self.parent, "Σφάλμα", "Δεν βρέθηκε ημερομηνία πληρωμής.")
            return

        payment_method = payment_method_item.text()
        subscription_package = subscription_package_item.text()
        date = date_item.text()
        confirmation = QMessageBox.question(
            self.parent,
            "Επιβεβαίωση Διαγραφής",
            f"Είστε σίγουροι ότι θέλετε να διαγράψετε την πληρωμη αυτή;",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirmation != QMessageBox.StandardButton.Yes:
            return
        # Αναζήτηση του ID της συνδρομής στη βάση δεδομένων
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT "κωδικός συνδρομής" 
                FROM "ΣΥΝΔΡΟΜΗ" 
                WHERE "τρόπος πληρωμής" = ? AND "πακέτο συνδρομής" = ?
            """, (payment_method, subscription_package))
            result = cursor.fetchone()

            if result is None:
                QMessageBox.warning(self.parent, "Σφάλμα", "Δεν βρέθηκε συνδρομή με τα δεδομένα που δώσατε.")
                return

            syndromi_id = result[0]

            # Διαγραφή της καταχώρησης
            cursor.execute("""
                DELETE FROM "ΜΕΛΟΣ_ΠΛΗΡΩΝΕΙ_ΣΥΝΔΡΟΜΗ"
                WHERE "κωδικός συνδρομής" = ? AND "μητρώο_μέλους" = ? AND "ημερομηνία πληρωμής" = ?
            """, (syndromi_id, member_id, date))
            conn.commit()

            # Ενημέρωση του πίνακα στο UI
            self.table.removeRow(row)
            QMessageBox.information(self.parent, "Επιτυχία", "Η καταχώρηση διαγράφηκε με επιτυχία.")

        except sqlite3.Error as e:
            QMessageBox.critical(self.parent, "Σφάλμα", f"Σφάλμα κατά τη διαγραφή: {e}")
            conn.rollback()

        finally:
            conn.close()

    def add_payment(self):
        # Ζήτηση μητρώου μέλους
        member_id, ok = QInputDialog.getText(self.parent, "Μητρώο Μέλους", "Εισάγετε το Μητρώο Μέλους:")
        if not ok or not member_id:
            QMessageBox.warning(self.parent, "Ακύρωση", "Δεν εισάγατε μητρώο μέλους.")
            return

        # Έλεγχος αν το μέλος υπάρχει
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM 'ΜΕΛΟΣ' WHERE μητρώο_μέλους = ?", (member_id,))
        if cursor.fetchone()[0] == 0:
            QMessageBox.warning(self.parent, "Σφάλμα", f"Το μέλος με μητρώο {member_id} δεν βρέθηκε στη βάση δεδομένων.")
            conn.close()
            return
        cursor.execute("SELECT COUNT(*) FROM 'ΑΜΕΙΒΟΜΕΝΟΣ ΠΑΙΚΤΗΣ' WHERE μητρώο_μέλους = ?", (member_id,))
        if cursor.fetchone()[0] > 0:
            QMessageBox.warning(self.parent, "Σφάλμα", f"Το μέλος με μητρώο {member_id} είναι αμειβόμενος παίκτης και δεν επιτρέπεται να πληρώσει συνδρομή.")
            conn.close()
            return
        # Ζήτηση τρόπου πληρωμής
        payment_method, ok = QInputDialog.getItem(
            self.parent, "Τρόπος Πληρωμής", "Επιλέξτε τρόπο πληρωμής:", ["Μετρητά", "Κάρτα"], 0, False
        )
        if not ok or not payment_method:
            QMessageBox.warning(self.parent, "Ακύρωση", "Δεν επιλέξατε τρόπο πληρωμής.")
            return

        # Ζήτηση ημερομηνίας πληρωμής
        payment_date, ok = QInputDialog.getText(self.parent, "Ημερομηνία Πληρωμής", "Εισάγετε την ημερομηνία πληρωμής (MM-YYYY):")
        if not ok or not payment_date:
            QMessageBox.warning(self.parent, "Ακύρωση", "Δεν εισάγατε ημερομηνία πληρωμής.")
            return

        # Έλεγχος μορφής MM-YYYY
        if not re.match(r"^(0[1-9]|1[0-2])-\d{4}$", payment_date):
            QMessageBox.warning(self.parent, "Σφάλμα", "Η ημερομηνία πληρωμής πρέπει να είναι στη μορφή MM-YYYY.")
            return

        # Αποθήκευση ακριβώς όπως δόθηκε (MM-YYYY)
        try:
            payment_month = datetime.strptime(payment_date, "%m-%Y")
            if payment_month > datetime.now():
                QMessageBox.warning(self.parent, "Σφάλμα", "Η ημερομηνία πληρωμής δεν μπορεί να είναι στο μέλλον.")
                return
        except ValueError:
            QMessageBox.warning(self.parent, "Σφάλμα", "Η ημερομηνία πληρωμής είναι μη έγκυρη.")
            return

        # Εύρεση του πακέτου συνδρομής
        # Έλεγχος αν το μέλος είναι "Παίκτης της Ομάδας"
        cursor.execute("SELECT COUNT(*) FROM 'ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ' WHERE μητρώο_μέλους = ?", (member_id,))
        if cursor.fetchone()[0] > 0:
            subscription_package = "Παίκτης της Ομάδας"
        else:
            # Έλεγχος αν το μέλος είναι "Ξένος Παίκτης"
            cursor.execute("SELECT COUNT(*) FROM 'ΞΕΝΟΣ ΠΑΙΚΤΗΣ' WHERE μητρώο_μέλους = ?", (member_id,))
            if cursor.fetchone()[0] > 0:
                subscription_package = "Ξένος Παίκτης"
            else:
                cursor.execute("""
                SELECT '2 αδέλφια' 
                FROM 'ΜΕΛΟΣ' 
                WHERE μητρώο_μέλους = ? AND πλήθος_αδελφών = 1
            """, (member_id,))
                result = cursor.fetchone()
                if result:
                    subscription_package = result[0]
                else:
                    cursor.execute("""
                    SELECT '3 αδέλφια'
                    FROM 'ΜΕΛΟΣ'
                    WHERE μητρώο_μέλους = ? AND πλήθος_αδελφών >= 2
                """, (member_id,))
                    result = cursor.fetchone()
                    if result:
                        subscription_package = result[0]
                    else:
                        # Προεπιλογή σε "Κανονική"
                        subscription_package = "Κανονικη"

        # Εύρεση κωδικού συνδρομής
        cursor.execute(
            """
            SELECT "κωδικός συνδρομής" FROM "ΣΥΝΔΡΟΜΗ"
            WHERE "τρόπος πληρωμής" = ? AND "πακέτο συνδρομής" = ?
            """,
            (payment_method, subscription_package)
        )
        result = cursor.fetchone()

        if result is None:
            QMessageBox.warning(self.parent, "Σφάλμα", "Δεν βρέθηκε συνδρομή με τα δεδομένα που δώσατε.")
            conn.close()
            return

        subscription_id = result[0]

        # Εισαγωγή εγγραφής στον πίνακα "ΜΕΛΟΣ_ΠΛΗΡΩΝΕΙ_ΣΥΝΔΡΟΜΗ"
        try:
            cursor.execute(
                """
                INSERT INTO ΜΕΛΟΣ_ΠΛΗΡΩΝΕΙ_ΣΥΝΔΡΟΜΗ ("κωδικός συνδρομής", "μητρώο_μέλους", "ημερομηνία πληρωμής")
                VALUES (?, ?, ?)
                """,
                (subscription_id, member_id, payment_date)  # Αποθήκευση σε μορφή MM-YYYY
            )
            conn.commit()
            QMessageBox.information(self.parent, "Επιτυχία", "Η πληρωμή καταχωρήθηκε επιτυχώς.")
                        # Ανάκτηση της γραμμής
            cursor.execute(
                f"""
                SELECT "{Melos.table_name}"."μητρώο_μέλους",
                    "{Melos.table_name}"."όνομα",
                    "{Melos.table_name}"."επώνυμο",
                    "{Syndromi.table_name}"."τρόπος πληρωμής",
                    "{Syndromi.table_name}"."πακέτο συνδρομής",
                    20*(
                        0.8*("{self.table_name}"."κωδικός συνδρομής"=1 OR "{self.table_name}"."κωδικός συνδρομής"=6) +
                        0.7*("{self.table_name}"."κωδικός συνδρομής"=2 OR "{self.table_name}"."κωδικός συνδρομής"=7) +
                        1.1*("{self.table_name}"."κωδικός συνδρομής"=3 OR "{self.table_name}"."κωδικός συνδρομής"=8) +
                        0.6*("{self.table_name}"."κωδικός συνδρομής"=4 OR "{self.table_name}"."κωδικός συνδρομής"=9) +
                        1*("{self.table_name}"."κωδικός συνδρομής"=5 OR "{self.table_name}"."κωδικός συνδρομής"=10)
                    ) AS "ποσό",
                    "{self.table_name}"."ημερομηνία πληρωμής"
                FROM "{self.table_name}"
                JOIN "{Melos.table_name}"
                ON "{Melos.table_name}"."μητρώο_μέλους" = "{self.table_name}"."μητρώο_μέλους"
                JOIN "{Syndromi.table_name}"
                ON "{Syndromi.table_name}"."κωδικός συνδρομής" = "{self.table_name}"."κωδικός συνδρομής"
                WHERE "{self.table_name}"."μητρώο_μέλους" = ? AND "{self.table_name}"."ημερομηνία πληρωμής" = ?
                """,
                (member_id, payment_date)
            )

            # Ανάκτηση της γραμμής
            new_row_data = cursor.fetchone()
            if not new_row_data:
                QMessageBox.warning(self.parent, "Σφάλμα", "Η νέα εγγραφή δεν βρέθηκε για προσθήκη στον πίνακα.")
                return



            new_date = datetime.strptime(payment_date, "%m-%Y")
            row_position = 0  # Default position is at the top

            for row in range(self.table.rowCount()):
                existing_date_item = self.table.item(row, 6)  # Στήλη της ημερομηνίας πληρωμής
                if existing_date_item is None:
                    continue

                existing_date = datetime.strptime(existing_date_item.text(), "%m-%Y")
                if new_date > existing_date:
                    row_position = row
                    break
                else:
                    row_position = row + 1

            # Εισαγωγή της νέας γραμμής στη σωστή θέση
            self.table.insertRow(row_position)

            # Τοποθέτηση δεδομένων στη νέα γραμμή
            for col_idx, value in enumerate(new_row_data):
                self.table.setItem(row_position, col_idx, QTableWidgetItem(str(value)))

            # Δημιουργία κουμπιού διαγραφής
            delete_button = QPushButton("Διαγραφή")
            delete_button.setStyleSheet(self.Buttonstylesheet)
            delete_button.clicked.connect(lambda checked, row=row_position: self.delete_entry(row))
            self.table.setCellWidget(row_position, 7, delete_button)
            #self.show_debts_table()
        except sqlite3.IntegrityError as e:
            QMessageBox.warning(self.parent, "Σφάλμα", f"Αποτυχία καταχώρησης πληρωμής: {e}")
        finally:
            conn.close()


    def show_debts_table(self):
        self.backButton = QPushButton("Επιστροφή")
        self.backButton.setStyleSheet(self.Buttonstylesheet)
        self.backButton.clicked.connect(self.go_back)
        query = (f"""
    SELECT 
        "{Melos.table_name}"."μητρώο_μέλους",
        "{Melos.table_name}"."όνομα",
        "{Melos.table_name}"."επώνυμο",
        "{Syndromi.table_name}"."τρόπος πληρωμής",
        "{Syndromi.table_name}"."πακέτο συνδρομής",
        20 * (
            0.8 * CASE WHEN "{self.table_name}"."κωδικός συνδρομής" IN (1, 6) THEN 1 ELSE 0 END +
            0.7 * CASE WHEN "{self.table_name}"."κωδικός συνδρομής" IN (2, 7) THEN 1 ELSE 0 END +
            1.1 * CASE WHEN "{self.table_name}"."κωδικός συνδρομής" IN (3, 8) THEN 1 ELSE 0 END +
            0.6 * CASE WHEN "{self.table_name}"."κωδικός συνδρομής" IN (4, 9) THEN 1 ELSE 0 END +
            1.0 * CASE WHEN "{self.table_name}"."κωδικός συνδρομής" IN (5, 10) THEN 1 ELSE 0 END
        ) AS "ποσό",
        MAX("{self.table_name}"."ημερομηνία πληρωμής") AS "τελευταία πληρωμή"
    FROM "{self.table_name}"
    JOIN "{Melos.table_name}"
        ON "{Melos.table_name}"."μητρώο_μέλους" = "{self.table_name}"."μητρώο_μέλους"
    JOIN "{Syndromi.table_name}"
        ON "{Syndromi.table_name}"."κωδικός συνδρομής" = "{self.table_name}"."κωδικός συνδρομής"
    GROUP BY 
        "{Melos.table_name}"."μητρώο_μέλους",
        "{Melos.table_name}"."όνομα",
        "{Melos.table_name}"."επώνυμο",
        "{Syndromi.table_name}"."τρόπος πληρωμής",
        "{Syndromi.table_name}"."πακέτο συνδρομής"
    ORDER BY 
    CAST(SUBSTR(MAX("{self.table_name}"."ημερομηνία πληρωμής"), 4, 4) AS INTEGER) DESC, -- Εξαγωγή έτους
    CAST(SUBSTR(MAX("{self.table_name}"."ημερομηνία πληρωμής"), 1, 2) AS INTEGER) DESC 
""")


        # Καθαρισμός του layout του tabSyndromi
        layout = self.parent.tabSyndromi.layout()
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

        # Δημιουργούμε έναν νέο πίνακα
        self.table = QTableWidget()
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        # Ρυθμίσεις του πίνακα
        self.table.setRowCount(len(rows))
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Μητρώο Μέλους", "Όνομα", "Επώνυμο", "Τρόπος Πληρωμής",
            "Πακέτο Συνδρομής", "Ποσό", "Τελευταία Πληρωμή", "Κατάσταση"
        ])


        today = datetime.today().strftime("%m-%Y")  # Λήψη τρέχοντος μήνα και έτους (π.χ., "09-2024")

        for row_idx, row_data in enumerate(rows):
            has_paid = row_data[-1].endswith(today)  # Έλεγχος αν η ημερομηνία πληρωμής είναι αυτόν τον μήνα
            color = QColor("green") if has_paid else QColor("red")  # Χρήση QColor για το χρώμα

            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setBackground(color)  # Ορίζει το χρώμα του κελιού
                self.table.setItem(row_idx, col_idx, item)

            # Κατάσταση: "Πληρωμένο" ή "Οφειλή"
            status = "Πληρωμένο" if has_paid else "Οφειλή"
            status_item = QTableWidgetItem(status)
            status_item.setBackground(color)
            self.table.setItem(row_idx, 7, status_item)  # Στήλη Κατάσταση

        # Προσθήκη του πίνακα και του κουμπιού "Επιστροφή"
        layout.addWidget(self.table)

        # Προσθέτουμε ξανά το κουμπί "Επιστροφή"
        layout.addWidget(self.backButton)

        self.table_shown = True

    def search_member(self):
        
        search_text = self.search_bar.text()

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        query = f"""SELECT "{Melos.table_name}"."μητρώο_μέλους",
        "{Melos.table_name}"."όνομα",
        "{Melos.table_name}"."επώνυμο",
        "{Syndromi.table_name}"."τρόπος πληρωμής",
        "{Syndromi.table_name}"."πακέτο συνδρομής",20*(
        0.8*("{self.table_name}"."κωδικός συνδρομής"=1 OR "{self.table_name}"."κωδικός συνδρομής"=6) +
        0.7*("{self.table_name}"."κωδικός συνδρομής"=2 OR "{self.table_name}"."κωδικός συνδρομής"=7) +
        1.1*("{self.table_name}"."κωδικός συνδρομής"=3 OR "{self.table_name}"."κωδικός συνδρομής"=8) +
        0.6*("{self.table_name}"."κωδικός συνδρομής"=4 OR "{self.table_name}"."κωδικός συνδρομής"=9) +
        1*("{self.table_name}"."κωδικός συνδρομής"=5 OR "{self.table_name}"."κωδικός συνδρομής"=10))
        AS "ποσό",
        "{self.table_name}"."ημερομηνία πληρωμής"
    FROM 
        "{self.table_name}"
    JOIN 
        "{Melos.table_name}"
    ON 
        "{Melos.table_name}"."μητρώο_μέλους" = "{self.table_name}"."μητρώο_μέλους"
    JOIN 
        "{Syndromi.table_name}"
    ON 
        "{Syndromi.table_name}"."κωδικός συνδρομής" = "{self.table_name}"."κωδικός συνδρομής"
    WHERE "{Melos.table_name}"."μητρώο_μέλους" LIKE ? OR 
        "{Melos.table_name}"."όνομα" LIKE ? OR
        "{Melos.table_name}"."επώνυμο" LIKE ? OR
        "{Syndromi.table_name}"."τρόπος πληρωμής" LIKE ? OR
        "ποσό" LIKE ?
    ORDER BY 
        CAST(SUBSTR("{self.table_name}"."ημερομηνία πληρωμής", 4, 4) AS INTEGER) DESC,
        CAST(SUBSTR("{self.table_name}"."ημερομηνία πληρωμής", 1, 2) AS INTEGER) DESC   
"""

        cursor.execute(query, (f"%{search_text}%", f"%{search_text}%", f"%{search_text}%",f"%{search_text}%", f"%{search_text}%"))
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))

        for row in range(len(rows)):
            for column, value in enumerate(rows[row]):
                item = QTableWidgetItem(str(value))
                item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)  # Μη επεξεργάσιμο στοιχείο
                self.table.setItem(row, column, item)
            if self.table.cellWidget(row,7 ):
                self.table.cellWidget(row, 7).deleteLater()

            delete_button = QPushButton("Διαγραφή")
            delete_button.setStyleSheet(self.Buttonstylesheet)
            delete_button.clicked.connect(lambda checked, row=row: self.delete_member(row))

            self.table.setCellWidget(row, 7, delete_button)
