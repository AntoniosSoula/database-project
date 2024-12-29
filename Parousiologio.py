import sqlite3
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QMessageBox, QInputDialog
from PyQt6.QtCore import Qt
from Melos import *
from PyQt6.QtGui import QColor
import re
from Prosopiko import *
from Melos import *
class ProponitisProponeiMelos(Prosopiko,Melos):
    table_name='ΠΡΟΠΟΝΗΤΗΣ_ΠΡΟΠΟΝΕΙ_ΜΕΛΟΣ'
    def __init__(self,parent):
        Prosopiko.__init__(self,parent)
        Melos.__init__(self,parent)
    
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

            # Ενεργοποίηση του κουμπιού "Πίνακας Μελών"
            self.parent.buttonParousiologio.setEnabled(True)
    def show_table(self):
        query = (f"""SELECT "{self.table_name}"."email",
        "{self.table_name}"."μητρώο_μέλους",
        "{Melos.table_name}"."όνομα",
        "{Melos.table_name}"."επώνυμο",
        "{self.table_name}"."ημερομηνία προπόνησης",
        "{self.table_name}."κατάσταση"
        
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
        CAST(SUBSTR("{self.table_name}"."ημερομηνία προπόνησης", 7, 4) AS INTEGER) DESC,
        CAST(SUBSTR("{self.table_name}"."ημερομηνία προπόνησης", 4, 2) AS INTEGER) DESC,
        CAST(SUBSTR("{self.table_name}"."ημερομηνία προπόνησης", 1, 2) AS INTEGER) DESC
 
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
        self.table.setColumnCount(7)  
        self.table.setHorizontalHeaderLabels([
            "Προπονητής","Μητρώο Μέλους", "Όνομα", "Επώνυμο",  "Ημερομηνία Προπόνησης","Κατάσταση","Διαγραφή"]
        )

        # Γεμίζουμε τον πίνακα με δεδομένα
        for row, row_data in enumerate(rows):
            for column, value in enumerate(row_data):
                self.table.setItem(row, column, QTableWidgetItem(str(value)))

            # Δημιουργία κουμπιού για Διαγραφή
            delete_button = QPushButton("Διαγραφή")
            delete_button.setStyleSheet(self.Buttonstylesheet)
            delete_button.clicked.connect(lambda checked, row=row: self.delete_entry(row))
            self.table.setCellWidget(row, 6, delete_button)  


        layout = self.parent.tabParousiologio.layout()
        if layout is None:
            layout = QVBoxLayout()
            self.parent.tabParousiologio.setLayout(layout)

        layout.addWidget(self.table)
        layout.addWidget(self.backButton)
        self.table_shown = True

        # Δημιουργία και σύνδεση του κουμπιού για προσθήκη νέας εγγραφής
        self.addButton = QPushButton("Προσθήκη Παρουσίας")
        self.addButton.setStyleSheet(self.Buttonstylesheet)
        self.addButton.clicked.connect(self.add_presence)
        layout.addWidget(self.addButton)

    def delete_entry(self, row):
        item = self.table.item(row, 1)
        if item is None:  # Έλεγχος αν το κελί είναι κενό
            QMessageBox.warning(self.parent, "Σφάλμα", "Δεν βρέθηκε το στοιχείο για διαγραφή.")
            return

        member_id = item.text()
        date_item = self.table.item(row, 4)
        coach_email_item=self.table.item(row,0)

        if coach_email_item is None:
            QMessageBox.warning(self.parent, "Σφάλμα", "Δεν βρέθηκε προπονητής.")
            return
        if date_item is None:
            QMessageBox.warning(self.parent, "Σφάλμα", "Δεν βρέθηκε ημερομηνία προπόνησης.")
            return

        coach_email=coach_email_item.text()
        date = date_item.text()

        # Αναζήτηση του ID της συνδρομής στη βάση δεδομένων
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            # Διαγραφή της καταχώρησης
            cursor.execute(f"""
                DELETE FROM "{self.table_name}"
                WHERE "email" = ? AND "μητρώο_μέλους" = ? AND "ημερομηνία προπόνησης" = ?
            """, (coach_email, member_id, date))
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
        return
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
        # Ζήτηση τρόπου πληρωμής
        payment_method, ok = QInputDialog.getItem(
            self.parent, "Τρόπος Πληρωμής", "Επιλέξτε τρόπο πληρωμής:",
            ["Μετρητά", "Κάρτα"], 0, False
        )
        if not ok or not payment_method:
            QMessageBox.warning(self.parent, "Ακύρωση", "Δεν επιλέξατε τρόπο πληρωμής.")
            return

        payment_date, ok = QInputDialog.getText(self.parent, "Ημερομηνία Πληρωμής", "Εισάγετε την ημερομηνία πληρωμής (MM-YYYY):")
        if not ok or not payment_date:
            QMessageBox.warning(self.parent, "Ακύρωση", "Δεν εισάγατε ημερομηνία πληρωμής.")
            return

        # Έλεγχος μορφής MM-YYYY
    
        if not re.match(r"^(0[1-9]|1[0-2])-\d{4}$", payment_date):
            QMessageBox.warning(self.parent, "Σφάλμα", "Η ημερομηνία πληρωμής πρέπει να είναι στη μορφή MM-YYYY.")
            return

        # Προαιρετικός έλεγχος αν η ημερομηνία είναι μελλοντική

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
            SELECT '2 Αδέλφια' 
            FROM 'ΜΕΛΟΣ' 
            WHERE μητρώο_μέλους = ? AND πλήθος_αδελφών = 1
        """, (member_id,))
                result = cursor.fetchone()
                if result:
                    subscription_package = result[0]
                else:
                    cursor.execute("""
                SELECT '3 Αδέλφια'
                FROM 'ΜΕΛΟΣ'
                WHERE μητρώο_μέλους = ? AND πλήθος_αδελφών >= 2
            """, (member_id,))
                    result = cursor.fetchone()
                    if result:
                        subscription_package = result[0]
                    else:
                # Προεπιλογή σε "Κανονική"
                        subscription_package = "Κανονική"
        # Εύρεση κωδικού συνδρομής
        cursor.execute(
            """
            SELECT "κωδικός συνδρομής" FROM ΣΥΝΔΡΟΜΗ
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
                (subscription_id, member_id, payment_date)
            )
            conn.commit()
            QMessageBox.information(self.parent, "Επιτυχία", "Η πληρωμή καταχωρήθηκε επιτυχώς.")
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


        except sqlite3.IntegrityError as e:
            QMessageBox.warning(self.parent, "Σφάλμα", f"Αποτυχία καταχώρησης πληρωμής: {e}")
        finally:
            conn.close()

