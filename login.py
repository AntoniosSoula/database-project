import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import sqlite3
from database import *
import sys
class Login:
    def __init__(self):
        self.window = None
        self.entry_username = None
        self.entry_password = None
        self.bg_photo = None
        self.role = None

    def create_database(self):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        """)
        # Προσθήκη κάποιων χρηστών
        cursor.execute("INSERT OR IGNORE INTO users VALUES ('g_xouridas', '1234', 'Προπονητής')")
        cursor.execute("INSERT OR IGNORE INTO users VALUES ('a_soula', '1234', 'Προπονητής')")
        cursor.execute("INSERT OR IGNORE INTO users VALUES ('tziantopoulou', '5678', 'Γραμματέας')")
        cursor.execute("INSERT OR IGNORE INTO users VALUES ('georgiou_v', '147', 'Πρόεδρος')")
        conn.commit()
        conn.close()

    def check_login(self, username, password):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE username = ? AND password = ?", (username, password))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        self.role = self.check_login(username, password)
        if self.role:
            messagebox.showinfo("Επιτυχία", f"Καλωσήρθες, {self.role}!")
            self.window.destroy()
        else:
            messagebox.showerror("Σφάλμα", "Λάθος όνομα χρήστη ή κωδικός.")

    def main_page(self):
        self.window = tk.Tk()
        self.window.title("Σύστημα Σύνδεσης")
        self.window.geometry("800x600")

        # Προσθήκη εικόνας φόντου
        bg_image = Image.open("pingpong.webp")
        bg_image = bg_image.resize((800, 600), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(bg_image)

        bg_label = tk.Label(self.window, image=self.bg_photo)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        frame = tk.Frame(self.window, bg="#31363F", relief="solid", padx=30, pady=30, highlightbackground="#222831", highlightthickness=5)
        frame.pack(pady=150)

        tk.Label(frame, text="Όνομα Χρήστη:", bg="#31363F", font=("Arial", 12), fg="white").pack(anchor="w", pady=5)
        self.entry_username = tk.Entry(frame, width=30, bd=1)
        self.entry_username.pack(pady=5)

        tk.Label(frame, text="Κωδικός:", bg="#31363F", font=("Arial", 12), fg="white").pack(anchor="w", pady=5)
        self.entry_password = tk.Entry(frame, show="*", width=30, bd=1)
        self.entry_password.pack(pady=5)

        tk.Button(frame, text="Σύνδεση", command=self.login, font=("Arial", 12), bg="#76ABAE", fg="white",
                  relief="raised", padx=10, pady=5, bd=3, highlightthickness=0).pack(pady=10)

        self.window.mainloop()

    def run(self):
        self.create_database()
        self.main_page()
        return self.role

    def exit_application(self):
        """Κλείσιμο εφαρμογής από το login"""
        self.window.destroy()
        sys.exit()  # Κλείσιμο ολόκληρης της εφαρμογής
