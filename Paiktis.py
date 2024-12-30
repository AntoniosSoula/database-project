import sys
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QMessageBox, QInputDialog
import sqlite3
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QDate
from Melos import Melos
class TeamPaiktis(Melos):
    table_name = "ΠΑΙΚΤΗΣ"
    table2_name = "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ"

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
                    "{super().table_name}"."μητρώο_μέλους", 
                    "{super().table_name}"."όνομα", 
                    "{super().table_name}"."επώνυμο", 
                    "{super().table_name}"."ημερομηνία_γέννησης", 
                    "{super().table_name}"."επίπεδο", 
                    "{super().table_name}"."τηλέφωνο", 
                    "{super().table_name}"."φύλο", 
                    "{super().table_name}"."πλήθος_αδελφών", 
                    "{self.table_name}"."RN", 
                    "{self.table_name}"."Δελτίο_ΑΘλητή", 
                    "{self.table2_name}"."ήττες", 
                    "{self.table2_name}"."νίκες", 
                    "{self.table2_name}"."points", 
                    "{self.table2_name}"."κατηγορία"
                FROM "{self.table_name}"
                JOIN "{super().table_name}" 
                    ON "{self.table_name}"."μητρώο_μέλους" = "{super().table_name}"."μητρώο_μέλους"
                JOIN "{self.table2_name}"
                    ON "{self.table_name}"."μητρώο_μέλους" = "{self.table2_name}"."μητρώο_μέλους"
            """
            cursor.execute(query)
            rows = cursor.fetchall()

            column_names = ["Μητρώο Μέλους","Όνομα","Επώνυμο","Ημερομηνία Γέννησης","Επίπεδο","Τηλέφωνο","Φύλο","Πλήθος Αδερφών","RN","Δελτίο Αθλητή","Ήττες","Νίκες","Πόντοι","Κατηγορία"]
            conn.close()

            self.table.setRowCount(len(rows))
            self.table.setColumnCount(len(column_names) + 2)  # +2 για τις στήλες Διαγραφή και Ενημέρωση
            self.table.setHorizontalHeaderLabels(column_names + ["Διαγραφή", "Ενημέρωση"])

            for row in range(len(rows)):
                for column, value in enumerate(rows[row]):
                    item = QTableWidgetItem(str(value))
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)  # Μη επεξεργάσιμο στοιχείο
                    self.table.setItem(row, column, item)

                # Προσθήκη κουμπιών "Διαγραφή" και "Ενημέρωση"
                delete_button = QPushButton("Διαγραφή")
                update_button = QPushButton("Ενημέρωση")
                delete_button.setStyleSheet(self.Buttonstylesheet)
                update_button.setStyleSheet(self.Buttonstylesheet)        
                delete_button.clicked.connect(lambda checked, row=row: self.delete_member(row))
                update_button.clicked.connect(lambda checked, row=row: self.update_member(row))        
                self.table.setCellWidget(row, len(column_names), delete_button)
                self.table.setCellWidget(row, len(column_names)+1, update_button)

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

            self.addButton = QPushButton("Προσθήκη Παίκτη της Ομάδας")
            self.addButton.setStyleSheet(self.Buttonstylesheet)
            self.addButton.clicked.connect(self.add_member)
            layout.addWidget(self.addButton)
    def search_member(self):
        
        search_text = self.searchBar.text()

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        query = f"""
                SELECT
                    "{super().table_name}"."μητρώο_μέλους", 
                    "{super().table_name}"."όνομα", 
                    "{super().table_name}"."επώνυμο", 
                    "{super().table_name}"."ημερομηνία_γέννησης", 
                    "{super().table_name}"."επίπεδο", 
                    "{super().table_name}"."τηλέφωνο", 
                    "{super().table_name}"."φύλο", 
                    "{super().table_name}"."πλήθος_αδελφών", 
                    "{self.table_name}"."RN", 
                    "{self.table_name}"."Δελτίο_ΑΘλητή", 
                    "{self.table2_name}"."ήττες", 
                    "{self.table2_name}"."νίκες", 
                    "{self.table2_name}"."points", 
                    "{self.table2_name}"."κατηγορία"
                FROM "{self.table_name}"
                JOIN "{super().table_name}" 
                    ON "{self.table_name}"."μητρώο_μέλους" = "{super().table_name}"."μητρώο_μέλους"
                JOIN "{self.table2_name}"
                    ON "{self.table_name}"."μητρώο_μέλους" = "{self.table2_name}"."μητρώο_μέλους"
                WHERE "{super().table_name}"."μητρώο_μέλους" LIKE ? OR
                    "{super().table_name}"."όνομα" LIKE ? OR "{super().table_name}"."επώνυμο" LIKE ? OR
                    "{super().table_name}"."ημερομηνία_γέννησης" LIKE ? OR
                    "{super().table_name}"."επίπεδο" LIKE ? OR
                    "{super().table_name}"."τηλέφωνο" LIKE ? OR
                    "{super().table_name}"."φύλο" LIKE ? OR
                    "{self.table_name}"."RN" LIKE ? OR
                     "{self.table2_name}"."κατηγορία" LIKE ?
                    
                
            """

        cursor.execute(query, (f"%{search_text}%", f"%{search_text}%", f"%{search_text}%",f"%{search_text}%", f"%{search_text}%", f"%{search_text}%",f"%{search_text}%", f"%{search_text}%", f"%{search_text}%"))
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))

        for row in range(len(rows)):
            for column, value in enumerate(rows[row]):
                item = QTableWidgetItem(str(value))
                item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)  # Μη επεξεργάσιμο στοιχείο
                self.table.setItem(row, column, item)

            delete_button = QPushButton("Διαγραφή")
            update_button = QPushButton("Ενημέρωση")
            delete_button.setStyleSheet(self.Buttonstylesheet)
            update_button.setStyleSheet(self.Buttonstylesheet)

            delete_button.clicked.connect(lambda checked, row=row: self.delete_member(row))
            update_button.clicked.connect(lambda checked, row=row: self.update_member(row))
            if self.table.cellWidget(row, 14):
                self.table.cellWidget(row, 14).deleteLater()
            if self.table.cellWidget(row, 15):
                self.table.cellWidget(row, 15).deleteLater()
            self.table.setCellWidget(row, 14, delete_button)
            self.table.setCellWidget(row, 15, update_button)
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
        cursor.execute(f"""
            SELECT * FROM "{super().table_name}"
            WHERE "μητρώο_μέλους" = ?
        """, (μητρώο_μέλους,))
        member_data = cursor.fetchone()

        if not member_data:  # Εάν το μητρώο μέλους δεν βρέθηκε στον πίνακα "ΜΕΛΟΣ"
            QMessageBox.warning(self.parent, "Σφάλμα", "Δεν βρέθηκε το μέλος με το συγκεκριμένο μητρώο.")
            conn.close()
            return

        # Έλεγχος αν το μητρώο_μέλους υπάρχει ήδη στον πίνακα "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ"
        cursor.execute(f"""
            SELECT * FROM "{self.table2_name}"
            WHERE "μητρώο_μέλους" = ?
        """, (μητρώο_μέλους,))
        player_in_team = cursor.fetchone()

        if player_in_team:  # Αν το μητρώο μέλους υπάρχει ήδη στον πίνακα "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ"
            QMessageBox.warning(self.parent, "Σφάλμα", "Το μέλος ανήκει ήδη στην ομάδα ως παίκτης.")
            conn.close()
            return

        # Έλεγχος αν το μητρώο_μέλους υπάρχει ήδη στον πίνακα "ΞΕΝΟΣ ΠΑΙΚΤΗΣ"
        cursor.execute(f"""
            SELECT * FROM "ΞΕΝΟΣ ΠΑΙΚΤΗΣ"
            WHERE "μητρώο_μέλους" = ?
        """, (μητρώο_μέλους,))
        foreign_player = cursor.fetchone()

        if foreign_player:  # Αν το μητρώο μέλους υπάρχει ήδη στον πίνακα "ΞΕΝΟΣ ΠΑΙΚΤΗΣ"
            QMessageBox.warning(self.parent, "Σφάλμα", "Ο παίκτης είναι ήδη ξένος παίκτης.")
            conn.close()
            return
        try:
            
            cursor.execute(f"""
                INSERT INTO "{self.table_name}" ("RN", "μητρώο_μέλους")
                VALUES (?, ?)
            """, (RN, μητρώο_μέλους))

            
            cursor.execute(f"""
                INSERT INTO "{self.table2_name}" ("μητρώο_μέλους", "ήττες", "νίκες", "points", "κατηγορία")
                VALUES (?, 0, 0, 0, "")
            """, (μητρώο_μέλους,))

            # Επιβεβαίωση αλλαγών στη βάση
            conn.commit()

            # Εκτέλεση ενός query για να ανακτήσουμε όλα τα δεδομένα του νέου παίκτη από τους πίνακες
            cursor.execute(f"""
                        SELECT
                            "{super().table_name}"."μητρώο_μέλους", 
                            "{super().table_name}"."όνομα", 
                            "{super().table_name}"."επώνυμο", 
                            "{super().table_name}"."ημερομηνία_γέννησης", 
                            "{super().table_name}"."επίπεδο", 
                            "{super().table_name}"."τηλέφωνο", 
                            "{super().table_name}"."φύλο", 
                            "{super().table_name}"."πλήθος_αδελφών",
                            "{self.table_name}"."RN", 
                            "{self.table_name}"."Δελτίο_ΑΘλητή", 
                            "{self.table2_name}"."ήττες", 
                            "{self.table2_name}"."νίκες", 
                            "{self.table2_name}"."points", 
                            "{self.table2_name}"."κατηγορία"
                        FROM "{self.table_name}"
                        JOIN "{super().table_name}" 
                            ON "{self.table_name}"."μητρώο_μέλους" = "{super().table_name}"."μητρώο_μέλους"
                        JOIN "{self.table2_name}" 
                            ON "{self.table_name}"."μητρώο_μέλους" = "{self.table2_name}"."μητρώο_μέλους"
                        WHERE "{self.table_name}"."μητρώο_μέλους" = ?
            """, (μητρώο_μέλους,))

            row = cursor.fetchone()  # Παίρνουμε την τελευταία γραμμή (νέο μέλος)

            # Προσθήκη του νέου παίκτη στον πίνακα του UI
            row_position = self.table.rowCount()  # Λήψη του αριθμού γραμμών
            self.table.insertRow(row_position)  # Προσθήκη νέας γραμμής
            for item in range(len(row)):
                if isinstance(row[item],str):
                    Item=QTableWidgetItem(row[item])
                    Item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                    self.table.setItem(row_position, item, Item)  
                elif isinstance(row[item],int) or isinstance(row[item],float) :
                    Item=QTableWidgetItem(str(row[item]))
                    Item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                    self.table.setItem(row_position, item, Item) 
                else:
                    Item=QTableWidgetItem(str("None"))
                    Item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)                    
                    self.table.setItem(row_position, item, Item)  # Μητρώο Μέλους
            # Ρύθμιση των κελιών με τα νέα δεδομένα

            # Δημιουργία κουμπιών "Διαγραφή" και "Ενημέρωση" για τη νέα γραμμή
            delete_button = QPushButton("Διαγραφή")
            update_button = QPushButton("Ενημέρωση")

            # Χρησιμοποιούμε default arguments για να δεσμεύσουμε την τρέχουσα τιμή της row_position
            delete_button.clicked.connect(lambda checked, row=row_position: self.delete_member(row))
            update_button.clicked.connect(lambda checked, row=row_position: self.update_member(row))

            self.table.setCellWidget(row_position, len(row), delete_button)  # Διαγραφή στην στήλη 12
            self.table.setCellWidget(row_position, len(row) + 1, update_button)  # Ενημέρωση στην στήλη 13
            delete_button.setStyleSheet(self.Buttonstylesheet)
            update_button.setStyleSheet(self.Buttonstylesheet)


            QMessageBox.information(self.parent, "Επιτυχία", f"Ο παίκτης με μητρώο {μητρώο_μέλους} προστέθηκε στην ομάδα.")

        except sqlite3.Error as e:
            QMessageBox.critical(self.parent, "Σφάλμα", f"Σφάλμα κατά την εισαγωγή του παίκτη: {e}")

        finally:
            conn.close()

    def update_member(self, row):
        # Επιλέγουμε το μητρώο του μέλους και ζητάμε νέα δεδομένα για ενημέρωση
        member_id = self.table.item(row, 0).text()  # Το μητρώο_μέλους είναι στην πρώτη στήλη του πίνακα
        
    
        column_names = [
           "Επώνυμο", "Όνομα", "Ημερομηνία Γέννησης", "Επίπεδο", 
            "Τηλέφωνο", "Φύλο", "Πλήθος Αδερφών", "Δελτίο Αθλητή", "RN", 
            "Ήττες", "Νίκες", "Points", "Κατηγορία"
        ]
        
        # Περνάμε την parent (QDialog) ως το πρώτο όρισμα
        column_index, ok = QInputDialog.getInt(
            self.parent,  # parent πρέπει να είναι το QDialog (δηλαδή self.parent)
            "Επιλογή Πεδίου", 
            "Διάλεξε στήλη για ενημέρωση (1-13):\n" + "\n".join([f"{i+1}. {name}" for i, name in enumerate(column_names)]),
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
        
        try:
            # Ελέγχουμε τη σύνδεση στη βάση και τη σωστή εκτέλεση του query
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()

 
            if column_index < 7:
                columns_db = ["επώνυμο", "όνομα", "ημερομηνία_γέννησης", "επίπεδο", "τηλέφωνο", "φύλο", "πλήθος_αδελφών"]
               
                cursor.execute(
                    f"""UPDATE "{super().table_name}" SET {columns_db[column_index]} = ? WHERE μητρώο_μέλους = ?""",
                    (new_value, member_id)
                )


            elif column_index == 7 or column_index == 8:
                columns_db = ["Δελτίο_ΑΘλητή", "RN"]
                
                cursor.execute(
                    f"""UPDATE "{self.table_name}" SET {columns_db[column_index-7]} = ? WHERE μητρώο_μέλους = ?""",
                    (new_value, member_id)
                )


            elif column_index >= 9:
                columns_db = ["ήττες", "νίκες", "points", "κατηγορία"]
              
                cursor.execute(
                    f"""UPDATE "{self.table2_name}" SET {columns_db[column_index-9]} = ? WHERE μητρώο_μέλους = ?""",
                    (new_value, member_id)
                )

            conn.commit()  # Αποθηκεύουμε τις αλλαγές

        except sqlite3.Error as e:
            # Σε περίπτωση σφάλματος κατά την εκτέλεση της ενημέρωσης
            QMessageBox.warning(self.parent, "Σφάλμα", f"Σφάλμα κατά την ενημέρωση της βάσης: {e}")
        
        finally:
            # Κλείσιμο της σύνδεσης στη βάση
            conn.close()

            # Ενημέρωση του πίνακα στο UI
            self.table.setItem(row, column_index + 1, QTableWidgetItem(new_value))
            print(f"Το μέλος με μητρώο {member_id} ενημερώθηκε.")
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

            cursor.execute(f"""DELETE FROM "{self.table_name}" WHERE μητρώο_μέλους = ?""", (member_id,))
            
            cursor.execute(f"""DELETE FROM "{self.table2_name}" WHERE μητρώο_μέλους = ?""", (member_id,))
            cursor.execute(f"""DELETE FROM "ΑΜΕΙΒΟΜΕΝΟΣ ΠΑΙΚΤΗΣ" WHERE μητρώο_μέλους = ?""", (member_id,))

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
class ΝοTeamPaiktis(Melos):
    table_name="ΠΑΙΚΤΗΣ"
    table2_name="ΞΕΝΟΣ ΠΑΙΚΤΗΣ"
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
        "{super().table_name}"."μητρώο_μέλους",
        "{super().table_name}"."όνομα", 
        "{super().table_name}"."επώνυμο", 
        "{super().table_name}"."ημερομηνία_γέννησης", 
        "{super().table_name}"."επίπεδο", 
        "{super().table_name}"."τηλέφωνο", 
        "{super().table_name}"."φύλο", 
        "{super().table_name}"."πλήθος_αδελφών",
        "{self.table_name}"."RN", 
        "{self.table_name}"."Δελτίο_ΑΘλητή", 
        "{self.table2_name}"."ομάδα"
    FROM "{self.table_name}"
    JOIN "{super().table_name}" 
        ON "{self.table_name}"."μητρώο_μέλους" = "{super().table_name}"."μητρώο_μέλους"
    JOIN "{self.table2_name}"
        ON "{self.table_name}"."μητρώο_μέλους" = "{self.table2_name}"."μητρώο_μέλους"
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

# Ρύθμιση των κελιών με τα νέα δεδομένα
            for row in range(len(rows)):
                for column, value in enumerate(rows[row]):
                    self.table.setItem(row, column, QTableWidgetItem(str(value)))

            # Δημιουργία κουμπιών "Διαγραφή" και "Ενημέρωση" για τη νέα γραμμή
                delete_button = QPushButton("Διαγραφή")
                update_button = QPushButton("Ενημέρωση")

                delete_button.clicked.connect(lambda checked, row=row: self.delete_member(row))
                update_button.clicked.connect(lambda checked, row=row: self.update_member(row))

                self.table.setCellWidget(row, len(column_names), delete_button)  # Διαγραφή στην στήλη 12
                self.table.setCellWidget(row, len(column_names) + 1, update_button)  # Ενημέρωση στην στήλη 13

            layout = self.parent.tabMeli.layout()
            if layout is None:
                layout = QVBoxLayout()
                self.parent.tabMeli.setLayout(layout)

            layout.addWidget(self.table)
            layout.addWidget(self.backButton)
            self.table_shown = True
            self.addButton = QPushButton("Προσθήκη Ξένου Παίκτη")
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
        team, ok3 = QInputDialog.getText(self.parent, "Εισαγωγή Ομάδας", "Ομάδα Ξένου Παίκτη:")

        if not ok3 or not team:  # Εάν ο χρήστης δεν εισάγει την ομάδα
            QMessageBox.warning(self.parent, "Σφάλμα", "Πρέπει να εισάγεις την ομάδα.")
            return
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")

    # Έλεγχος αν το μητρώο_μέλους υπάρχει στον πίνακα "ΜΕΛΟΣ"
        cursor.execute(f"""
            SELECT * FROM "{super().table_name}"
            WHERE "μητρώο_μέλους" = ?
        """, (μητρώο_μέλους,))
        member_data = cursor.fetchone()

        if not member_data:  # Εάν το μητρώο μέλους δεν βρέθηκε στον πίνακα "ΜΕΛΟΣ"
            QMessageBox.warning(self.parent, "Σφάλμα", "Δεν βρέθηκε το μέλος με το συγκεκριμένο μητρώο.")
            conn.close()
            return

        # Έλεγχος αν το μητρώο_μέλους υπάρχει ήδη στον πίνακα "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ"
        cursor.execute(f"""
            SELECT * FROM "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ"
            WHERE "μητρώο_μέλους" = ?
        """, (μητρώο_μέλους,))
        player_in_team = cursor.fetchone()

        if player_in_team:  # Αν το μητρώο μέλους υπάρχει ήδη στον πίνακα "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ"
            QMessageBox.warning(self.parent, "Σφάλμα", "Το μέλος ανήκει ήδη στην ομάδα ως παίκτης.")
            conn.close()
            return

        # Έλεγχος αν το μητρώο_μέλους υπάρχει ήδη στον πίνακα "ΞΕΝΟΣ ΠΑΙΚΤΗΣ"
        cursor.execute(f"""
            SELECT * FROM "{self.table2_name}"
            WHERE "μητρώο_μέλους" = ?
        """, (μητρώο_μέλους,))
        foreign_player = cursor.fetchone()

        if foreign_player:  # Αν το μητρώο μέλους υπάρχει ήδη στον πίνακα "ΞΕΝΟΣ ΠΑΙΚΤΗΣ"
            QMessageBox.warning(self.parent, "Σφάλμα", "Ο παίκτης είναι ήδη ξένος παίκτης.")
            conn.close()
            return
        try:
            
            cursor.execute(f"""
                INSERT INTO "{self.table_name}" ("RN", "μητρώο_μέλους")
                VALUES (?, ?)
            """, (RN, μητρώο_μέλους))

            
            cursor.execute(f"""
                INSERT INTO "{self.table2_name}" ("μητρώο_μέλους", "ομάδα")
                VALUES (?,?)
            """, (μητρώο_μέλους,team))

            # Επιβεβαίωση αλλαγών στη βάση
            conn.commit()

            # Εκτέλεση ενός query για να ανακτήσουμε όλα τα δεδομένα του νέου παίκτη από τους πίνακες
            cursor.execute(f"""
                        SELECT
                            "{super().table_name}"."μητρώο_μέλους", 
                            "{super().table_name}"."όνομα", 
                            "{super().table_name}"."επώνυμο", 
                            "{super().table_name}"."ημερομηνία_γέννησης", 
                            "{super().table_name}"."επίπεδο", 
                            "{super().table_name}"."τηλέφωνο", 
                            "{super().table_name}"."φύλο", 
                            "{super().table_name}"."πλήθος_αδελφών",
                            "{self.table_name}"."RN", 
                            "{self.table_name}"."Δελτίο_ΑΘλητή", 
                            "{self.table2_name}"."ομάδα" 

                        FROM "{self.table_name}"
                        JOIN "{super().table_name}" 
                            ON "{self.table_name}"."μητρώο_μέλους" = "{super().table_name}"."μητρώο_μέλους"
                        JOIN "{self.table2_name}" 
                            ON "{self.table_name}"."μητρώο_μέλους" = "{self.table2_name}"."μητρώο_μέλους"
                        WHERE "{self.table_name}"."μητρώο_μέλους" = ?
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
        # Επιλέγουμε το μητρώο του μέλους και ζητάμε νέα δεδομένα για ενημέρωση
        member_id = self.table.item(row, 0).text()  # Το μητρώο_μέλους είναι στην πρώτη στήλη του πίνακα
        
    
        column_names = [
           "Επώνυμο", "Όνομα", "Ημερομηνία Γέννησης", "Επίπεδο", 
            "Τηλέφωνο", "Φύλο", "Πλήθος Αδερφών", "Δελτίο Αθλητή", "RN", 
            "Ομάδα"
        ]
        
        # Περνάμε την parent (QDialog) ως το πρώτο όρισμα
        column_index, ok = QInputDialog.getInt(
            self.parent,  # parent πρέπει να είναι το QDialog (δηλαδή self.parent)
            "Επιλογή Πεδίου", 
            "Διάλεξε στήλη για ενημέρωση (1-13):\n" + "\n".join([f"{i+1}. {name}" for i, name in enumerate(column_names)]),
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
        
        try:
            # Ελέγχουμε τη σύνδεση στη βάση και τη σωστή εκτέλεση του query
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()

 
            if column_index < 7:
                columns_db = ["επώνυμο", "όνομα", "ημερομηνία_γέννησης", "επίπεδο", "τηλέφωνο", "φύλο", "πλήθος_αδελφών"]
               
                cursor.execute(
                    f"""UPDATE "{super().table_name}" SET {columns_db[column_index]} = ? WHERE μητρώο_μέλους = ?""",
                    (new_value, member_id)
                )


            elif column_index == 7 or column_index == 8:
                columns_db = ["Δελτίο_ΑΘλητή", "RN"]
                
                cursor.execute(
                    f"""UPDATE "{self.table_name}" SET {columns_db[column_index-7]} = ? WHERE μητρώο_μέλους = ?""",
                    (new_value, member_id)
                )


            elif column_index >= 9:
                columns_db = ["ομάδα"]
              
                cursor.execute(
                    f"""UPDATE "{self.table2_name}" SET {columns_db[column_index-9]} = ? WHERE μητρώο_μέλους = ?""",
                    (new_value, member_id)
                )

            conn.commit()  # Αποθηκεύουμε τις αλλαγές

        except sqlite3.Error as e:
            # Σε περίπτωση σφάλματος κατά την εκτέλεση της ενημέρωσης
            QMessageBox.warning(self.parent, "Σφάλμα", f"Σφάλμα κατά την ενημέρωση της βάσης: {e}")
        
        finally:
            # Κλείσιμο της σύνδεσης στη βάση
            conn.close()

            # Ενημέρωση του πίνακα στο UI
            self.table.setItem(row, column_index + 1, QTableWidgetItem(new_value))
            print(f"Το μέλος με μητρώο {member_id} ενημερώθηκε.")
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

            cursor.execute(f"""DELETE FROM "{self.table_name}" WHERE μητρώο_μέλους = ?""", (member_id,))
            
            cursor.execute(f"""DELETE FROM "{self.table2_name}" WHERE μητρώο_μέλους = ?""", (member_id,))


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
class PaiktisAmeivomenos(TeamPaiktis):
    table_name="ΑΜΕΙΒΟΜΕΝΟΣ ΠΑΙΚΤΗΣ"
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
        "{Melos.table_name}"."μητρώο_μέλους",  -- Πίνακας ΜΕΛΟΣ
        "{Melos.table_name}"."όνομα", 
        "{Melos.table_name}"."επώνυμο", 
        "{Melos.table_name}"."τηλέφωνο", 
        "{super().table_name}"."RN",  -- Πίνακας ΠΑΙΚΤΗΣ
        "{self.table_name}"."ΑΦΜ",  -- Πίνακας ΑΜΕΙΒΟΜΕΝΟΣ ΠΑΙΚΤΗΣ
        "{self.table_name}"."αμοιβή", 
        "{self.table_name}"."ημερομηνία έναρξης συμβολαίου", 
        "{self.table_name}"."ημερομηνία λήξης συμβολαίου",
        "{self.table_name}"."IBAN"
    FROM "{self.table_name}"  -- ΑΜΕΙΒΟΜΕΝΟΣ ΠΑΙΚΤΗΣ
    JOIN "{Melos.table_name}" 
        ON "{self.table_name}"."μητρώο_μέλους" = "{Melos.table_name}"."μητρώο_μέλους"  -- JOIN με ΜΕΛΟΣ
    JOIN "{super().table_name}"  -- JOIN με ΠΑΙΚΤΗΣ
        ON "{self.table_name}"."μητρώο_μέλους" = "{super().table_name}"."μητρώο_μέλους"
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

    # Ρύθμιση των κελιών με τα νέα δεδομένα
            for row in range(len(rows)):
                for column, value in enumerate(rows[row]):
                    self.table.setItem(row, column, QTableWidgetItem(str(value)))

            # Δημιουργία κουμπιών "Διαγραφή" και "Ενημέρωση" για τη νέα γραμμή
                delete_button = QPushButton("Διαγραφή")
                update_button = QPushButton("Ενημέρωση")

                delete_button.clicked.connect(lambda checked, row=row: self.delete_member(row))
                update_button.clicked.connect(lambda checked, row=row: self.update_member(row))

                self.table.setCellWidget(row, len(column_names), delete_button)  # Διαγραφή στην στήλη 12
                self.table.setCellWidget(row, len(column_names) + 1, update_button)  # Ενημέρωση στην στήλη 13

            layout = self.parent.tabMeli.layout()
            if layout is None:
                layout = QVBoxLayout()
                self.parent.tabMeli.setLayout(layout)

            layout.addWidget(self.table)
            layout.addWidget(self.backButton)
            self.table_shown = True
            self.addButton = QPushButton("Προσθήκη Αμειβόμενου Παίκτη")
            self.addButton.setStyleSheet(self.Buttonstylesheet)
            self.addButton.clicked.connect(self.add_member)
            layout.addWidget(self.addButton)
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

            cursor.execute(f"""DELETE FROM "{self.table_name}" WHERE μητρώο_μέλους = ?""", (member_id,))
            
            cursor.execute(f"""DELETE FROM "{super().table2_name}" WHERE μητρώο_μέλους = ?""", (member_id,))
            cursor.execute(f"""DELETE FROM "{super().table_name}" WHERE μητρώο_μέλους = ?""", (member_id,))



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
    def add_member(self):
        # Ζήτα από τον χρήστη το μητρώο μέλους
        μητρώο_μέλους, ok1 = QInputDialog.getText(self.parent, "Εισαγωγή Μητρώου Μέλους", "Μητρώο Μέλους:")
        if not ok1 or not μητρώο_μέλους:
            QMessageBox.warning(self.parent, "Σφάλμα", "Πρέπει να εισάγεις το μητρώο μέλους.")
            return

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")

        # Έλεγχος αν το μητρώο_μέλους υπάρχει στον πίνακα "ΜΕΛΟΣ"
        cursor.execute(f"""
            SELECT * FROM "ΜΕΛΟΣ"
            WHERE "μητρώο_μέλους" = ?
        """, (μητρώο_μέλους,))
        member_data = cursor.fetchone()

        if not member_data:
            QMessageBox.warning(self.parent, "Σφάλμα", "Δεν βρέθηκε το μέλος με το συγκεκριμένο μητρώο.")
            conn.close()
            return

        # Έλεγχος αν το μητρώο_μέλους υπάρχει ήδη στον πίνακα "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ"
        cursor.execute(f"""
            SELECT * FROM "{self.table2_name}"
            WHERE "μητρώο_μέλους" = ?
        """, (μητρώο_μέλους,))
        player_in_team = cursor.fetchone()

        # Έλεγχος αν το μητρώο_μέλους υπάρχει ήδη στον πίνακα "ΞΕΝΟΣ ΠΑΙΚΤΗΣ"
        cursor.execute(f"""
            SELECT * FROM "ΞΕΝΟΣ ΠΑΙΚΤΗΣ"
            WHERE "μητρώο_μέλους" = ?
        """, (μητρώο_μέλους,))
        foreign_player = cursor.fetchone()

        if player_in_team:  # Αν το μέλος ανήκει ήδη στον πίνακα "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ"
            cursor.execute(f"""
                SELECT "{super().table_name}"."RN"
                FROM "{super().table_name}"
                WHERE "{super().table_name}"."μητρώο_μέλους" = ?
            """, (μητρώο_μέλους,))
            player_data = cursor.fetchone()
            RN = player_data[0]  # Αντλούμε το RN

            # Ζητάμε τα δεδομένα του αμειβόμενου παίκτη (ΑΦΜ, αμοιβή, ημερομηνία έναρξης, λήξης συμβολαίου, IBAN)
            ΑΦΜ, ok3 = QInputDialog.getText(self.parent, "Εισαγωγή ΑΦΜ", "ΑΦΜ:")
            if len(ΑΦΜ) != 9 or not ΑΦΜ.isdigit():
                QMessageBox.warning(self.parent, "Σφάλμα", "Μη έγκυρο ΑΦΜ. Πρέπει να έχει 9 ψηφία.")
                return
            
            αμοιβή, ok4 = QInputDialog.getText(self.parent, "Εισαγωγή Αμοιβής", "Αμοιβή:")
            try:
                float(αμοιβή)  # Έλεγχος αν η αμοιβή είναι αριθμός
            except ValueError:
                QMessageBox.warning(self.parent, "Σφάλμα", "Η αμοιβή πρέπει να είναι αριθμός.")
                return
            
            ημερομηνία_έναρξης, ok5 = QInputDialog.getText(self.parent, "Ημερομηνία Έναρξης Συμβολαίου", "Ημερομηνία Έναρξης Συμβολαίου (yyyy-MM-dd):")
            if not QDate.fromString(ημερομηνία_έναρξης, "yyyy-MM-dd").isValid():
                QMessageBox.warning(self.parent, "Σφάλμα", "Μη έγκυρη ημερομηνία έναρξης.")
                return
            
            ημερομηνία_λήξης, ok6 = QInputDialog.getText(self.parent, "Ημερομηνία Λήξης Συμβολαίου", "Ημερομηνία Λήξης Συμβολαίου (yyyy-MM-dd):")
            if not QDate.fromString(ημερομηνία_λήξης, "yyyy-MM-dd").isValid():
                QMessageBox.warning(self.parent, "Σφάλμα", "Μη έγκυρη ημερομηνία λήξης.")
                return
            start_date = QDate.fromString(ημερομηνία_έναρξης, "yyyy-MM-dd")
            end_date = QDate.fromString(ημερομηνία_λήξης, "yyyy-MM-dd")

            # Ελέγχουμε αν οι ημερομηνίες είναι έγκυρες
            if not start_date.isValid() or not end_date.isValid():
                QMessageBox.warning(self.parent, "Σφάλμα", "Μη έγκυρη ημερομηνία. Βεβαιωθείτε ότι οι ημερομηνίες είναι σωστές.")
                return

            # Σύγκριση των ημερομηνιών
            if end_date > start_date:  # Αν η ημερομηνία λήξης είναι μεγαλύτερη από την ημερομηνία έναρξης
                # Η ημερομηνία λήξης είναι μετά από την ημερομηνία έναρξης, συνεχίζουμε
                pass
            else:
                # Η ημερομηνία λήξης είναι μικρότερη ή ίση με την ημερομηνία έναρξης
                QMessageBox.warning(self.parent, "Σφάλμα", "Η ημερομηνία λήξης πρέπει να είναι μετά την ημερομηνία έναρξης.")
                return            
            IBAN, ok7 = QInputDialog.getText(self.parent, "Εισαγωγή IBAN", "IBAN:")
            if len(IBAN) != 27:
                QMessageBox.warning(self.parent, "Σφάλμα", "Μη έγκυρο IBAN.")
                return

            # Εισαγωγή στον πίνακα "ΑΜΕΙΒΟΜΕΝΟΣ ΠΑΙΚΤΗΣ"
            cursor.execute(f"""
                INSERT INTO "{self.table_name}" ("μητρώο_μέλους", "ΑΦΜ", "αμοιβή", "ημερομηνία έναρξης συμβολαίου", "ημερομηνία λήξης συμβολαίου", "IBAN")
                VALUES (?, ?, ?, ?, ?, ?)
            """, (μητρώο_μέλους, ΑΦΜ, αμοιβή, ημερομηνία_έναρξης, ημερομηνία_λήξης, IBAN))

        elif foreign_player:  # Αν το μέλος είναι ήδη ΞΕΝΟΣ ΠΑΙΚΤΗΣ
            QMessageBox.warning(self.parent, "Σφάλμα", "Ο παίκτης είναι ήδη ξένος παίκτης.")
            conn.close()
            return
        else:  # Αν το μέλος δεν ανήκει σε καμία από τις προηγούμενες κατηγορίες, το προσθέτουμε ως νέο παίκτη
            RN, ok2 = QInputDialog.getText(self.parent, "Εισαγωγή RN", "RN:")
            if not ok2 or not RN:
                QMessageBox.warning(self.parent, "Σφάλμα", "Πρέπει να εισάγεις το RN.")
                return

            cursor.execute(f"""
                INSERT INTO "{super().table_name}" ("RN", "μητρώο_μέλους")
                VALUES (?, ?)
            """, (RN, μητρώο_μέλους))

            cursor.execute(f"""
                INSERT INTO "{super().table2_name}" ("μητρώο_μέλους", "ήττες", "νίκες", "points", "κατηγορία")
                VALUES (?, 0, 0, 0, "")
            """, (μητρώο_μέλους,))

            conn.commit()

            cursor.execute(f"""
                SELECT "{super().table_name}"."RN"
                FROM "{super().table_name}"
                WHERE "{super().table_name}"."μητρώο_μέλους" = ?
            """, (μητρώο_μέλους,))
            player_data = cursor.fetchone()
            RN = player_data[0]  # Αντλούμε το RN

            # Ζητάμε τα δεδομένα του αμειβόμενου παίκτη
            ΑΦΜ, ok3 = QInputDialog.getText(self.parent, "Εισαγωγή ΑΦΜ", "ΑΦΜ:")
            if len(ΑΦΜ) != 9 or not ΑΦΜ.isdigit():
                QMessageBox.warning(self.parent, "Σφάλμα", "Μη έγκυρο ΑΦΜ. Πρέπει να έχει 9 ψηφία.")
                return
            
            αμοιβή, ok4 = QInputDialog.getText(self.parent, "Εισαγωγή Αμοιβής", "Αμοιβή:")
            try:
                float(αμοιβή)  # Έλεγχος αν η αμοιβή είναι αριθμός
                if float(αμοιβή) < 0:
                    QMessageBox.warning(self.parent, "Σφάλμα", "Η αμοιβή πρέπει να είναι θετικός αριθμός.")
                    return
            except ValueError:
                QMessageBox.warning(self.parent, "Σφάλμα", "Η αμοιβή πρέπει να είναι αριθμός.")
                return
            start_date = QDate.fromString(ημερομηνία_έναρξης, "yyyy-MM-dd")
            end_date = QDate.fromString(ημερομηνία_λήξης, "yyyy-MM-dd")

            # Ελέγχουμε αν οι ημερομηνίες είναι έγκυρες
            if not start_date.isValid() or not end_date.isValid():
                QMessageBox.warning(self.parent, "Σφάλμα", "Μη έγκυρη ημερομηνία. Βεβαιωθείτε ότι οι ημερομηνίες είναι σωστές.")
                return

            # Σύγκριση των ημερομηνιών
            if not end_date > start_date:  # Αν η ημερομηνία λήξης είναι μεγαλύτερη από την ημερομηνία έναρξης
                QMessageBox.warning(self.parent, "Σφάλμα", "Η ημερομηνία λήξης πρέπει να είναι μετά την ημερομηνία έναρξης.")
                return
# Αν η ημερομηνία λήξης είναι έγκυρη, προχωράμε
# ... Συνεχίζουμε με την επεξεργασία του υπόλοιπου κώδικα.

            IBAN, ok7 = QInputDialog.getText(self.parent, "Εισαγωγή IBAN", "IBAN:")
            if len(IBAN) != 27:
                QMessageBox.warning(self.parent, "Σφάλμα", "Μη έγκυρο IBAN.")
                return

            # Εισαγωγή στον πίνακα "ΑΜΕΙΒΟΜΕΝΟΣ ΠΑΙΚΤΗΣ"
            cursor.execute(f"""
                INSERT INTO "{self.table_name}" ("μητρώο_μέλους", "ΑΦΜ", "αμοιβή", "ημερομηνία έναρξης συμβολαίου", "ημερομηνία λήξης συμβολαίου", "IBAN")
                VALUES (?, ?, ?, ?, ?, ?)
            """, (μητρώο_μέλους, ΑΦΜ, αμοιβή, ημερομηνία_έναρξης, ημερομηνία_λήξης, IBAN))

        conn.commit()
        QMessageBox.information(self.parent, "Επιτυχία", f"Ο παίκτης με μητρώο {μητρώο_μέλους} προστέθηκε ως Αμειβόμενος Παίκτης.")

        try:
            query = f"""
                SELECT
                    "{Melos.table_name}"."μητρώο_μέλους",  -- Πίνακας ΜΕΛΟΣ
                    "{Melos.table_name}"."όνομα", 
                    "{Melos.table_name}"."επώνυμο", 
                    "{Melos.table_name}"."τηλέφωνο", 
                    "{super().table_name}"."RN",  -- Πίνακας ΠΑΙΚΤΗΣ
                    "{self.table_name}"."ΑΦΜ",  -- Πίνακας ΑΜΕΙΒΟΜΕΝΟΣ ΠΑΙΚΤΗΣ
                    "{self.table_name}"."αμοιβή", 
                    "{self.table_name}"."ημερομηνία έναρξης συμβολαίου", 
                    "{self.table_name}"."ημερομηνία λήξης συμβολαίου",
                    "{self.table_name}"."IBAN"
                FROM "{self.table_name}"  -- ΑΜΕΙΒΟΜΕΝΟΣ ΠΑΙΚΤΗΣ
                JOIN "{Melos.table_name}" 
                    ON "{self.table_name}"."μητρώο_μέλους" = "{Melos.table_name}"."μητρώο_μέλους"  -- JOIN με ΜΕΛΟΣ
                JOIN "{super().table_name}"  -- JOIN με ΠΑΙΚΤΗΣ
                    ON "{self.table_name}"."μητρώο_μέλους" = "{super().table_name}"."μητρώο_μέλους"
                WHERE "{self.table_name}"."μητρώο_μέλους" = ?
            """
            cursor.execute(query, (μητρώο_μέλους,))
            row = cursor.fetchone()  # Παίρνουμε την τελευταία γραμμή (νέο μέλος)

            if row is None:  # Ελέγχουμε αν δεν βρέθηκαν αποτελέσματα
                QMessageBox.warning(self.parent, "Σφάλμα", "Δεν βρέθηκαν δεδομένα για το μέλος με το μητρώο αυτό.")
                return
                # Προσθήκη του νέου παίκτη στον πίνακα του UI
                # Προσθήκη του νέου παίκτη στον πίνακα του UI
            
            row_position = self.table.rowCount()  # Λήψη του αριθμού γραμμών
            self.table.insertRow(row_position)  # Προσθήκη νέας γραμμής
            for item in range(len(row)):
                if isinstance(row[item], str):
                    self.table.setItem(row_position, item, QTableWidgetItem(row[item]))  # Μητρώο Μέλους
                elif isinstance(row[item], int) or isinstance(row[item], float):
                    self.table.setItem(row_position, item, QTableWidgetItem(str(row[item])))  # Μητρώο Μέλους
                else:
                    self.table.setItem(row_position, item, QTableWidgetItem(str("None")))  # Μητρώο Μέλους

            # Δημιουργία κουμπιών "Διαγραφή" και "Ενημέρωση" για τη νέα γραμμή
            delete_button = QPushButton("Διαγραφή")
            update_button = QPushButton("Ενημέρωση")

            delete_button.clicked.connect(lambda checked, row=row_position: self.delete_member(row_position))
            update_button.clicked.connect(lambda checked, row=row_position: self.update_member(row_position))

            self.table.setCellWidget(row_position, len(row), delete_button)  # Διαγραφή στην στήλη 12
            self.table.setCellWidget(row_position, len(row) + 1, update_button)  # Ενημέρωση στην στήλη 13

            QMessageBox.information(self.parent, "Επιτυχία", f"Ο παίκτης με μητρώο {μητρώο_μέλους} προστέθηκε στην ομάδα.")
        except sqlite3.Error as e:
            QMessageBox.critical(self.parent, "Σφάλμα", f"Σφάλμα κατά την εισαγωγή του παίκτη: {e}")
        finally:
            conn.close()
    def update_member(self, row):
        # Επιλέγουμε το μητρώο του μέλους και ζητάμε νέα δεδομένα για ενημέρωση
        member_id = self.table.item(row, 0).text()  # Το μητρώο_μέλους είναι στην πρώτη στήλη του πίνακα

        column_names = [
            "ΑΦΜ", "αμοιβή", "ημερομηνία έναρξης συμβολαίου", "ημερομηνία λήξης συμβολαίου", "IBAN"
        ]

        # Περνάμε την parent (QDialog) ως το πρώτο όρισμα
        column_index, ok = QInputDialog.getInt(
            self.parent,  # parent πρέπει να είναι το QDialog (δηλαδή self.parent)
            "Επιλογή Πεδίου", 
            "Διάλεξε στήλη για ενημέρωση (1-5):\n" + "\n".join([f"{i+1}. {name}" for i, name in enumerate(column_names)]),
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
        if column_index == 0:  # ΑΦΜ
            if len(new_value) != 9 or not new_value.isdigit():
                QMessageBox.warning(self.parent, "Σφάλμα", "Μη έγκυρο ΑΦΜ. Πρέπει να έχει 9 ψηφία.")
                return

        elif column_index == 1:  # Αμοιβή
            try:
                float(new_value)  # Έλεγχος αν η αμοιβή είναι αριθμός
                if float(new_value) < 0:
                    QMessageBox.warning(self.parent, "Σφάλμα", "Η αμοιβή πρέπει να είναι θετικός αριθμός.")
                    return
            except ValueError:
                QMessageBox.warning(self.parent, "Σφάλμα", "Η αμοιβή πρέπει να είναι αριθμός.")
                return

        elif column_index == 2 or column_index == 3:  # Ημερομηνία Έναρξης και Λήξης Συμβολαίου
            new_date = QDate.fromString(new_value, "yyyy-MM-dd")
            if not new_date.isValid():
                QMessageBox.warning(self.parent, "Σφάλμα", "Μη έγκυρη ημερομηνία. Βεβαιωθείτε ότι η ημερομηνία είναι σωστή.")
                return

            if column_index == 2:  # Έλεγχος όταν τροποποιείται η ημερομηνία έναρξης
                end_date_str = self.table.item(row, 3).text()  # Λαμβάνουμε την ημερομηνία λήξης από τον πίνακα
                if end_date_str:  # Ελέγχουμε αν υπάρχει ήδη ημερομηνία λήξης
                    end_date = QDate.fromString(end_date_str, "yyyy-MM-dd")
                    if end_date.isValid() and new_date >= end_date:  # Αν η ημερομηνία λήξης είναι έγκυρη, ελέγχουμε την ανισότητα
                        QMessageBox.warning(self.parent, "Σφάλμα", "Η ημερομηνία έναρξης πρέπει να είναι πριν την ημερομηνία λήξης.")
                        return

            elif column_index == 3:  # Έλεγχος όταν τροποποιείται η ημερομηνία λήξης
                start_date_str = self.table.item(row, 2).text()  # Λαμβάνουμε την ημερομηνία έναρξης από τον πίνακα
                if start_date_str:  # Ελέγχουμε αν υπάρχει ήδη ημερομηνία έναρξης
                    start_date = QDate.fromString(start_date_str, "yyyy-MM-dd")
                    if start_date.isValid() and new_date <= start_date:  # Αν η ημερομηνία έναρξης είναι έγκυρη, ελέγχουμε την ανισότητα
                        QMessageBox.warning(self.parent, "Σφάλμα", "Η ημερομηνία λήξης πρέπει να είναι μετά την ημερομηνία έναρξης.")
                        return

        elif column_index == 4:  # IBAN
            if len(new_value) != 27 or not new_value.startswith('GR'):
                QMessageBox.warning(self.parent, "Σφάλμα", "Μη έγκυρο IBAN. Πρέπει να έχει 27 χαρακτήρες και να ξεκινάει με 'GR'.")
                return

        try:
            # Ελέγχουμε τη σύνδεση στη βάση και τη σωστή εκτέλεση του query
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()

            # Εκτέλεση του UPDATE query για τον αμειβόμενο παίκτη
            columns_db = ["ΑΦΜ", "αμοιβή", "ημερομηνία έναρξης συμβολαίου", "ημερομηνία λήξης συμβολαίου", "IBAN"]
            cursor.execute(
                f"""UPDATE "{self.table_name}" SET "{columns_db[column_index]}" = ? WHERE μητρώο_μέλους = ?""",
                (new_value, member_id)
            )
            conn.commit()

            # Ενημέρωση του πίνακα UI
            self.table.setItem(row, column_index + 5, QTableWidgetItem(str(new_value)))
             # Αποθηκεύουμε τις αλλαγές

            # Ανακτούμε τα νέα δεδομένα από τη βάση και ενημερώνουμε τον πίνακα UI
           
            QMessageBox.information(self.parent, "Επιτυχία", f"Τα δεδομένα του παίκτη με μητρώο {member_id} ενημερώθηκαν.")
        except sqlite3.Error as e:
            QMessageBox.critical(self.parent, "Σφάλμα", f"Σφάλμα κατά την ενημέρωση της βάσης: {e}")
        finally:
            conn.close()