import sqlite3
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QTextEdit, QMessageBox
from datetime import datetime, timedelta

class IncomeExpenseViewer(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # Ρύθμιση του layout
        self.layout = self.parent.tabSyndromi.layout()
        if self.layout is None:
            self.layout = QVBoxLayout()
            self.parent.tabSyndromi.setLayout(self.layout)

        # Δημιουργία ComboBox
        self.comboBox = QComboBox(self.parent.tabSyndromi)
        self.comboBox.currentTextChanged.connect(self.update_income_expense)
        self.layout.addWidget(self.comboBox)

        # Δημιουργία TextEdit
        self.textEdit = QTextEdit(self.parent.tabSyndromi)
        self.textEdit.setReadOnly(True)
        self.layout.addWidget(self.textEdit)

        # Φόρτωση δεδομένων και ενημέρωση
        self.load_dates()
        self.update_income_expense()

    def load_dates(self):
        """ Φορτώνει τους μήνες και τα έτη από τον τρέχοντα μήνα μέχρι έναν χρόνο πριν. """
        current_date = datetime.now()
        self.comboBox.clear()  # Καθαρισμός προηγούμενων καταχωρίσεων

        # Δημιουργούμε λίστα μηνών από τον τρέχοντα μήνα έως έναν χρόνο πριν
        for i in range(12):
            month_year = (current_date - timedelta(days=i * 30)).strftime('%m-%Y')  # Μήνας-Έτος
            self.comboBox.addItem(month_year)

        # Ορίζουμε τον τρέχοντα μήνα ως προεπιλεγμένο
        self.comboBox.setCurrentText(current_date.strftime('%m-%Y'))

    def update_income_expense(self):
        """ Ενημερώνει τα έσοδα και τα έξοδα για τον επιλεγμένο μήνα και έτος. """
        selected_date = self.comboBox.currentText()
        if not selected_date:
            return

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:

            # Υπολογισμός εσόδων
            cursor.execute("""
            SELECT SUM(
                20 * (
                    0.8 * CASE WHEN "κωδικός συνδρομής" IN (1, 6) THEN 1 ELSE 0 END +
                    0.7 * CASE WHEN "κωδικός συνδρομής" IN (2, 7) THEN 1 ELSE 0 END +
                    1.1 * CASE WHEN "κωδικός συνδρομής" IN (3, 8) THEN 1 ELSE 0 END +
                    0.6 * CASE WHEN "κωδικός συνδρομής" IN (4, 9) THEN 1 ELSE 0 END +
                    1.0 * CASE WHEN "κωδικός συνδρομής" IN (5, 10) THEN 1 ELSE 0 END
                )
            )
            FROM "ΜΕΛΟΣ_ΠΛΗΡΩΝΕΙ_ΣΥΝΔΡΟΜΗ"
            WHERE "ημερομηνία πληρωμής" = ?
        """, (selected_date,))
            income = cursor.fetchone()[0] or 0  # Εξασφαλίζουμε ότι δεν θα είναι None

            # Υπολογισμός εξόδων
            cursor.execute("""
                SELECT SUM("ΠΡΟΣΩΠΙΚΟ"."αμοιβή")
                FROM "ΠΡΟΣΩΠΙΚΟ" JOIN "ΓΡΑΜΜΑΤΕΑΣ" ON "ΠΡΟΣΩΠΙΚΟ"."email" = "ΓΡΑΜΜΑΤΕΑΣ"."email"
            """)
            secretary_expenses = cursor.fetchone()[0] or 0

            cursor.execute("""
                SELECT SUM("αμοιβή"/12)
                FROM "ΑΜΕΙΒΟΜΕΝΟΣ ΠΑΙΚΤΗΣ"
            """)
            player_expenses = cursor.fetchone()[0] or 0

            cursor.execute("""
                SELECT SUM("ΠΡΟΣΩΠΙΚΟ"."αμοιβή" * (
                    SELECT COUNT(DISTINCT strftime('%d-%m-%Y', "ημερομηνία προπόνησης"))
                    FROM "ΠΡΟΠΟΝΗΤΗΣ_ΠΡΟΠΟΝΕΙ_ΜΕΛΟΣ"
                    WHERE strftime('%m-%Y', "ημερομηνία προπόνησης") = ?
                    AND "ΠΡΟΠΟΝΗΤΗΣ"."email" = "ΠΡΟΠΟΝΗΤΗΣ_ΠΡΟΠΟΝΕΙ_ΜΕΛΟΣ"."email"
                ))
                FROM "ΠΡΟΠΟΝΗΤΗΣ" JOIN "ΠΡΟΣΩΠΙΚΟ" ON "ΠΡΟΠΟΝΗΤΗΣ"."email" = "ΠΡΟΣΩΠΙΚΟ"."email"
            """, (selected_date,))
            coach_expenses = cursor.fetchone()[0] or 0

            total_expenses = secretary_expenses + player_expenses + coach_expenses

            # Εμφάνιση δεδομένων στο TextEdit
            self.textEdit.setText(
                f"Μήνας/Έτος: {selected_date}\n\n"
                f"Έσοδα: {income:.2f} €\n"
                f"Έξοδα: {total_expenses:.2f} €\n"
                f" - Γραμματείς: {secretary_expenses:.2f} €\n"
                f" - Αμειβόμενοι Παίκτες: {player_expenses:.2f} €\n"
                f" - Προπονητές: {coach_expenses:.2f} €\n"
            )

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Σφάλμα", f"Σφάλμα κατά τον υπολογισμό: {e}")
        finally:
            conn.close()
