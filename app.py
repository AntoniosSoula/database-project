import sys
from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6.uic import loadUi
from login import *

class Main(QDialog):
    def __init__(self,role,app):
        super().__init__()
        loadUi("untitled.ui", self)
        self.setFixedSize(self.size())
        self.setWindowTitle("Αθλητικός Όμιλος Ξυλοκάστρου")
        self.role = role  # Ο ρόλος του χρήστη
        self.app=app
        self.melos = None  # Αρχικοποιούμε το στιγμιότυπο της κλάσης Meli
        self.playerInTeam = None
        self.playerNoInTeam = None
        self.playerPaid = None
        self.subscription = None  # Προσθήκη της νέας μεταβλητής για το συνδρομητή
        self.employers=None
        self.melosplironeisyndromi=None
        self.proponitisproponeimelos=None
        self.income_expense_viewer=None
        # Συνδέουμε τα κουμπιά με τις αντίστοιχες μεθόδους
        self.buttonTableMeli.clicked.connect(self.show_member_table)
        self.buttonTablePaiktis.clicked.connect(self.show_teampaiktis_table)
        self.buttonTableNoInTeam.clicked.connect(self.show_no_teampaiktis_table)
        self.buttonTablePaidPaiktis.clicked.connect(self.show_paid_paiktis_table)
        self.buttonSyndromh.clicked.connect(self.show_subscription_table)  # Νέα σύνδεση για το κουμπί συνδρομητών
        self.buttonTablePaidPaiktis.clicked.connect(self.show_paid_paiktis_table)
        self.buttonTableProsopiko.clicked.connect(self.show_employees_table)
        self.buttonPliromon.clicked.connect(self.show_melos_plironei_syndromi_table)
        self.buttonParousiologio.clicked.connect(self.show_proponitis_proponei_melos)
        self.buttonEE.clicked.connect(self.show_income_expense_viewer)
        self.apply_role_restrictions()
    def closeEvent(self, event):
        """Χειρισμός κλεισίματος παραθύρου Main"""
        event.accept()  # Αποδοχή του κλεισίματος
        print("Main window closed. Reopening Login...")
        self.destroy()
        # Ανοίγει ξανά το Login
        login_app = Login()
        role = login_app.run()

        if role:  # Εάν η σύνδεση είναι επιτυχής
            new_window = Main(role, self.app)
            new_window.show()

    def show_member_table(self):
        from Melos import Melos  # Καθυστερημένη εισαγωγή
        if self.melos is None:
            self.melos = Melos(self)
        self.melos.show_table()
    def show_proponitis_proponei_melos(self):
        from Parousiologio import ProponitisProponeiMelos
        if self.proponitisproponeimelos is None:
            self.proponitisproponeimelos=ProponitisProponeiMelos(self)
        self.proponitisproponeimelos.show_table()
    def show_teampaiktis_table(self):
        from Paiktis import TeamPaiktis  # Καθυστερημένη εισαγωγή
        if self.playerInTeam is None:
            self.playerInTeam = TeamPaiktis(self)
        self.playerInTeam.show_table()

    def show_no_teampaiktis_table(self):
        from Paiktis import ΝοTeamPaiktis  # Καθυστερημένη εισαγωγή
        if self.playerNoInTeam is None:
            self.playerNoInTeam = ΝοTeamPaiktis(self)
        self.playerNoInTeam.show_table()

    def show_paid_paiktis_table(self):
        from Paiktis import PaiktisAmeivomenos  # Καθυστερημένη εισαγωγή
        if self.playerPaid is None:
            self.playerPaid = PaiktisAmeivomenos(self)
        self.playerPaid.show_table()

    def show_subscription_table(self):
        from Syndromi import Syndromi  # Καθυστερημένη εισαγωγή της κλάσης Syndromi
        if self.subscription is None:
            self.subscription = Syndromi(self)
        self.subscription.show_table()
    def show_employees_table(self):
        from Prosopiko import Prosopiko  # Καθυστερημένη εισαγωγή της κλάσης Syndromi
        if self.employers is None:
            self.employers = Prosopiko(self)
        self.employers.show_table()
    def show_melos_plironei_syndromi_table(self):
        from Syndromi import MelosPlironeiSyndromi
        if self.melosplironeisyndromi is None:
            self.melosplironeisyndromi=MelosPlironeiSyndromi(self)
        self.melosplironeisyndromi.show_table()
    def show_income_expense_viewer(self):
        from EsodaEksoda import IncomeExpenseViewer
        if not hasattr(self, 'income_expense_viewer') or self.income_expense_viewer is None:
            self.income_expense_viewer = IncomeExpenseViewer(self)
    def apply_role_restrictions(self):
        if self.role == "Προπονητής":
            # Απόκρυψη των tabs Syndromi και Prosopiko
            index_syndromi = self.tab.indexOf(self.tabSyndromi)
            if index_syndromi != -1:
                self.tab.removeTab(index_syndromi)

            index_prosopiko = self.tab.indexOf(self.tabProsopiko)
            if index_prosopiko != -1:
                self.tab.removeTab(index_prosopiko)

            # Απόκρυψη του κουμπιού buttonTablePaidPaiktis
            self.buttonTablePaidPaiktis.hide()
            
        if self.role == "Γραμματέας":
                    
            index_parousia = self.tab.indexOf(self.tabParousiologio)
            if index_parousia != -1:
                self.tab.removeTab(index_parousia)

            index_prosopiko = self.tab.indexOf(self.tabProsopiko)
            if index_prosopiko != -1:
                self.tab.removeTab(index_prosopiko)

            # Απόκρυψη του κουμπιού buttonTablePaidPaiktis
            self.buttonTablePaidPaiktis.hide()
            self.buttonEE.hide()
if __name__ == "__main__":
    while True:
        login_app = Login()
        role = login_app.run()
        if not role:  # Αν το login έκλεισε χωρίς σύνδεση
            break

        app = QApplication(sys.argv)
        main_window = Main(role, app)
        main_window.show()
        app.exec()
