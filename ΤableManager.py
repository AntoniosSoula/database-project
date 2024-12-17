import sys
from PyQt6.QtWidgets import (
    QApplication, QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QPushButton, QMessageBox, QInputDialog, QLineEdit, QDateEdit,
)
from PyQt6.uic import loadUi
import sqlite3
from functools import partial
from PyQt6.QtCore import QDate
from ΤableManager import *  # Βεβαιώσου ότι η κλάση TableManager βρίσκεται στο σωστό αρχείο και μονοπάτι

class TableManager:
    def __init__(self,table_name,column_names):
        self.table_name=table_name
        self.column_names=column_names

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
    
    def show_table(self,table_name,column_names):
        if self.table_shown:
            self.table.setParent(None)
            self.table_shown = False
        else:
            self.table = QTableWidget()
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            conn.close()

            self.table.setRowCount(len(rows))
            self.table.setColumnCount(len(column_names)+2)  # Προσθήκη στήλης ενημέρωσης
            self.table.setHorizontalHeaderLabels(column_names+["Διαγραφή","Ενημέρωση"])
            for row, row_data in enumerate(rows):
                for column, value in enumerate(row_data):
                    self.table.setItem(row, column, QTableWidgetItem(str(value)))

                # Κουμπί Διαγραφής
                delete_button = QPushButton("Διαγραφή")
                delete_button.clicked.connect(partial(self.delete_member, row))
                self.table.setCellWidget(row, len(column_names)+1, delete_button)

                # Κουμπί Ενημέρωσης
                update_button = QPushButton("Ενημέρωση")
                update_button.clicked.connect(partial(self.update_member, row))
                self.table.setCellWidget(row, len(column_names)+2, update_button)

            tab_index = self.tabWidget.indexOf(self.tabMeli)
            widget = self.tabWidget.widget(tab_index)
            layout = widget.layout()
            if layout is None:
                layout = QVBoxLayout()
                widget.setLayout(layout)
            layout.addWidget(self.table)
            layout.addWidget(self.backButton)
            self.table_shown = True

            # Εύρεση του layout του tab "Πίνακας Μελών"
            tab_index = self.tabWidget.indexOf(self.tabMeli)
            widget = self.tabWidget.widget(tab_index)
            layout = widget.layout()
            if layout is None:
                layout = QVBoxLayout()
                widget.setLayout(layout)

            # Προσθήκη του πίνακα και του κουμπιού "Προσθήκη Μέλους"
            layout.addWidget(self.table)
            self.addButton = QPushButton("Προσθήκη Μέλους")
            self.addButton.setStyleSheet(self.Buttonstylesheet)
            self.addButton.clicked.connect(self.add_member)
            layout.addWidget(self.addButton)

            layout.addWidget(self.backButton)
            self.table_shown = True
    def get_next_member_id(self):
        pass
    def add_member(self):
        pass
    def delete_member(self, row):
        pass
    def update_member(self, row):
        pass