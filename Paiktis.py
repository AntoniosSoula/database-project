import sys
from PyQt6.QtWidgets import QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QMessageBox, QInputDialog
from PyQt6.uic import loadUi
import sqlite3
from PyQt6.QtCore import QDate
from Melos import *

class TeamPaiktis(Melos):
    table_name="ΠΑΙΚΤΗΣ"
    table2_name="ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ"
    def __init__(self, parent):
        super().__init__(parent)

    def show_table(self):
        if self.table_shown:
            self.table.setParent(None)
            self.table_shown = False
        else:
            self.table = QTableWidget()
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            query = f"""
                    SELECT 
                        "ΜΕΛΟΣ"."όνομα", 
                        "ΜΕΛΟΣ"."επώνυμο", 
                        "ΜΕΛΟΣ"."ημερομηνία_γέννησης", 
                        "ΜΕΛΟΣ"."επίπεδο", 
                        "ΜΕΛΟΣ"."τηλέφωνο", 
                        "ΜΕΛΟΣ"."φύλο", 
                        "ΜΕΛΟΣ"."πλήθος_αδελφών",
                        "ΠΑΙΚΤΗΣ"."RN", 
                        "ΠΑΙΚΤΗΣ"."Δελτίο_ΑΘλητή", 
                        "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ"."ήττες", 
                        "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ"."νίκες", 
                        "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ"."points", 
                        "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ"."κατηγορία"
                    FROM "ΠΑΙΚΤΗΣ"
                    JOIN "ΜΕΛΟΣ" 
                        ON "ΠΑΙΚΤΗΣ"."μητρώο_μέλους" = "ΜΕΛΟΣ"."μητρώο_μέλους"
                    JOIN "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ" 
                        ON "ΠΑΙΚΤΗΣ"."μητρώο_μέλους" = "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ"."μητρώο_μέλους"
        """
            cursor.execute(query)
            rows = cursor.fetchall()

        # Λήψη δυναμικών στηλών
            column_names = [description[0] for description in cursor.description]

            conn.close()

        # Ρυθμίσεις για το QTableWidget
            self.table.setRowCount(len(rows))
            self.table.setColumnCount(len(column_names) + 2)  # +2 για τις στήλες Διαγραφή και Ενημέρωση
            self.table.setHorizontalHeaderLabels(column_names + ["Διαγραφή", "Ενημέρωση"])

            for row, row_data in enumerate(rows):
                for column, value in enumerate(row_data):
                    self.table.setItem(row, column, QTableWidgetItem(str(value)))
                
                # Δημιουργία κουμπιού για Διαγραφή και Ενημέρωση για κάθε γραμμή
                delete_button = QPushButton("Διαγραφή")
                update_button = QPushButton("Ενημέρωση")
                # Set the style from the loaded stylesheet

                # Σύνδεση των κουμπιών με τις αντίστοιχες μεθόδους
                delete_button.clicked.connect(lambda checked, row=row: self.delete_member(row))
                update_button.clicked.connect(lambda checked, row=row: self.update_member(row))

                self.table.setCellWidget(row, len(column_names), delete_button)  # Διαγραφή
                self.table.setCellWidget(row, len(column_names) + 1, update_button)
            # Προσθήκη του πίνακα στο tabMeli
            layout = self.parent.tabMeli.layout()
            if layout is None:
                layout = QVBoxLayout()
                self.parent.tabMeli.setLayout(layout)

            layout.addWidget(self.table)
            layout.addWidget(self.backButton)
            self.table_shown = True
            self.addButton = QPushButton("Προσθήκη Παίκτη της Ομάδας")
            self.addButton.setStyleSheet(self.Buttonstylesheet)
            self.addButton.clicked.connect(self.add_member)
            layout.addWidget(self.addButton)
    def add_member(self):
        # Ζήτα από τον χρήστη το μητρώο μέλους
        μητρώο_μέλους, ok1 = QInputDialog.getText(self.parent, "Εισαγωγή Μητρώου Μέλους", "Μητρώο Μέλους:")

        if not ok1 or not μητρώο_μέλους:  # Εάν ο χρήστης δεν εισάγει το μητρώο μέλους
            QMessageBox.warning(self.parent, "Σφάλμα", "Πρέπει να εισάγεις το μητρώο μέλους.")
            return

        # Ζήτα από τον χρήστη το RN
        RN, ok2 = QInputDialog.getText(self.parent, "Εισαγωγή RN", "RN:")

        if not ok2 or not RN:  # Εάν ο χρήστης δεν εισάγει το RN
            QMessageBox.warning(self.parent, "Σφάλμα", "Πρέπει να εισάγεις το RN.")
            return

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        # Έλεγχος αν το μητρώο_μέλους υπάρχει στον πίνακα "ΜΕΛΟΣ"
        cursor.execute("""
            SELECT * FROM "ΜΕΛΟΣ"
            WHERE "μητρώο_μέλους" = ?
        """, (μητρώο_μέλους,))
        member_data = cursor.fetchone()

        if not member_data:  # Εάν το μητρώο μέλους δεν βρέθηκε στον πίνακα "ΜΕΛΟΣ"
            QMessageBox.warning(self.parent, "Σφάλμα", "Δεν βρέθηκε το μέλος με το συγκεκριμένο μητρώο.")
            conn.close()
            return

        # Ανακτάς τα δεδομένα του μέλους από τον πίνακα "ΜΕΛΟΣ
        # Έλεγχος αν υπάρχει το μητρώο_μέλους στον πίνακα "ΠΑΙΚΤΗΣ"
        cursor.execute("""
            SELECT * FROM "ΠΑΙΚΤΗΣ"
            WHERE "μητρώο_μέλους" = ?
        """, (μητρώο_μέλους,))
        result = cursor.fetchone()

        if result:  # Εάν υπάρχει ήδη το μητρώο_μέλους στον πίνακα "ΠΑΙΚΤΗΣ"
            QMessageBox.warning(self.parent, "Σφάλμα", "Ο παίκτης υπάρχει ήδη στον πίνακα ΠΑΙΚΤΗΣ.")
            conn.close()
            return

        try:
            # Εισαγωγή του νέου παίκτη στον πίνακα "ΠΑΙΚΤΗΣ"
            cursor.execute("""
                INSERT INTO "ΠΑΙΚΤΗΣ" ("RN", "μητρώο_μέλους")
                VALUES (?, ?)
            """, (RN, μητρώο_μέλους))

            # Εισαγωγή στον πίνακα "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ" με τα default δεδομένα
            cursor.execute("""
                INSERT INTO "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ" ("μητρώο_μέλους", "ήττες", "νίκες", "points", "κατηγορία")
                VALUES (?, 0, 0, 0, "")
            """, (μητρώο_μέλους,))

            # Επιβεβαίωση αλλαγών στη βάση
            conn.commit()

            # Εκτέλεση ενός query για να ανακτήσουμε όλα τα δεδομένα του νέου παίκτη από τους πίνακες
            cursor.execute("""
                        SELECT 
                            "ΜΕΛΟΣ"."όνομα", 
                            "ΜΕΛΟΣ"."επώνυμο", 
                            "ΜΕΛΟΣ"."ημερομηνία_γέννησης", 
                            "ΜΕΛΟΣ"."επίπεδο", 
                            "ΜΕΛΟΣ"."τηλέφωνο", 
                            "ΜΕΛΟΣ"."φύλο", 
                            "ΜΕΛΟΣ"."πλήθος_αδελφών",
                            "ΠΑΙΚΤΗΣ"."RN", 
                            "ΠΑΙΚΤΗΣ"."Δελτίο_ΑΘλητή", 
                            "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ"."ήττες", 
                            "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ"."νίκες", 
                            "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ"."points", 
                            "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ"."κατηγορία"
                        FROM "ΠΑΙΚΤΗΣ"
                        JOIN "ΜΕΛΟΣ" 
                            ON "ΠΑΙΚΤΗΣ"."μητρώο_μέλους" = "ΜΕΛΟΣ"."μητρώο_μέλους"
                        JOIN "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ" 
                            ON "ΠΑΙΚΤΗΣ"."μητρώο_μέλους" = "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ"."μητρώο_μέλους"
                        WHERE "ΠΑΙΚΤΗΣ"."μητρώο_μέλους" = ?
            """, (μητρώο_μέλους,))

            row = cursor.fetchone()  # Παίρνουμε την τελευταία γραμμή (νέο μέλος)

            # Προσθήκη του νέου παίκτη στον πίνακα του UI
            row_position = self.table.rowCount()  # Λήψη του αριθμού γραμμών
            self.table.insertRow(row_position)  # Προσθήκη νέας γραμμής
            for item in range(len(row)):
                if isinstance(row[item],str):
                    self.table.setItem(row_position, item, QTableWidgetItem(row[item]))  # Μητρώο Μέλους
                elif isinstance(row[item],int) or isinstance(row[item],float) :
                    self.table.setItem(row_position, item, QTableWidgetItem(str(row[item])))  # Μητρώο Μέλους
                else:
                    self.table.setItem(row_position, item, QTableWidgetItem(str("None")))  # Μητρώο Μέλους
            # Ρύθμιση των κελιών με τα νέα δεδομένα

            # Δημιουργία κουμπιών "Διαγραφή" και "Ενημέρωση" για τη νέα γραμμή
            delete_button = QPushButton("Διαγραφή")
            update_button = QPushButton("Ενημέρωση")

            delete_button.clicked.connect(lambda checked, row=row_position: self.delete_member(row_position))
            update_button.clicked.connect(lambda checked, row=row_position: self.update_member(row_position))

            self.table.setCellWidget(row_position, len(row), delete_button)  # Διαγραφή στην στήλη 12
            self.table.setCellWidget(row_position, len(row)+1, update_button)  # Ενημέρωση στην στήλη 13

            QMessageBox.information(self.parent, "Επιτυχία", f"Ο παίκτης με μητρώο {μητρώο_μέλους} προστέθηκε στην ομάδα.")

        except sqlite3.Error as e:
            QMessageBox.critical(self.parent, "Σφάλμα", f"Σφάλμα κατά την εισαγωγή του παίκτη: {e}")

        finally:
            conn.close()

    def update_member(self, row):
        # Αναγνωρίζουμε το μητρώο μέλους
        member_id = self.table.item(row, 0).text()  # Υποθέτουμε ότι το μητρώο είναι στην 1η στήλη

        column_names = [
            "Επώνυμο", "Όνομα", "Ημερομηνία Γέννησης", "Επίπεδο",
            "Τηλέφωνο", "Φύλο", "Πλήθος Αδελφών", "RN",
            "Ήττες", "Νίκες", "Points", "Κατηγορία"
        ]
        
        # Ζητάμε από τον χρήστη ποιο πεδίο θέλει να ενημερώσει
        column_index, ok = QInputDialog.getInt(
            self.parent,
            "Επιλογή Πεδίου",
            "Διάλεξε στήλη για ενημέρωση (1-12):\n" + "\n".join([f"{i+1}. {name}" for i, name in enumerate(column_names)]),
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

        # Ελέγχοι για τα πεδία
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

        elif column_index == 6:  # Πλήθος Αδελφών
            if not new_value.isdigit() or int(new_value) < 0:
                QMessageBox.warning(self.parent, "Σφάλμα", "Μη έγκυρος αριθμός αδελφών.")
                return

        elif column_index == 7:  # RN (Δεν αλλάζει, δεν χρειάζεται να γίνει επεξεργασία εδώ)
            pass

        elif column_index == 8:  # Ήττες
            if not new_value.isdigit():
                QMessageBox.warning(self.parent, "Σφάλμα", "Μη έγκυρος αριθμός ήττων.")
                return

        elif column_index == 9:  # Νίκες
            if not new_value.isdigit():
                QMessageBox.warning(self.parent, "Σφάλμα", "Μη έγκυρος αριθμός νικών.")
                return

        elif column_index == 10:  # Points
            try:
                new_value = float(new_value)
            except ValueError:
                QMessageBox.warning(self.parent, "Σφάλμα", "Μη έγκυρο αριθμητικό πεδίο για points.")
                return

        elif column_index == 11:  # Κατηγορία
            pass  # Προσθήκη λογικής για έλεγχο αν απαιτείται

        # Ενημέρωση στους πίνακες "ΜΕΛΟΣ", "ΠΑΙΚΤΗΣ", "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ"
        if column_index < 7:  # Αναφορά στον πίνακα "ΜΕΛΟΣ"
            columns_db = ["επώνυμο", "όνομα", "ημερομηνία_γέννησης", "επίπεδο", "τηλέφωνο", "φύλο", "πλήθος_αδελφών"]
            table_name = "ΜΕΛΟΣ"
        elif column_index >= 8 and column_index < 11:  # "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ"
            columns_db = ["ήττες", "νίκες", "points"]
            table_name = "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ"
        else:
            columns_db = []  # Δεν χρειάζεται για άλλα πεδία αυτή τη στιγμή
            table_name = ""

        # Εκτέλεση του update query
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        try:
            cursor.execute(
                f" UPDATE {table_name} SET {columns_db[column_index]} = ? WHERE μητρώο_μέλους = ?;",
                (new_value, member_id)
            )

            conn.commit()

            # Ενημέρωση του πίνακα στο UI
            self.table.setItem(row, column_index + 1, QTableWidgetItem(str(new_value)))  # Ενημέρωση στο UI
            QMessageBox.information(self.parent, "Επιτυχία", f"Το πεδίο '{column_names[column_index]}' ενημερώθηκε επιτυχώς.")
        
        except sqlite3.Error as e:
            QMessageBox.warning(self.parent, "Σφάλμα", f"Σφάλμα κατά την ενημέρωση της βάσης: {e}")
        
        finally:
            conn.close()
