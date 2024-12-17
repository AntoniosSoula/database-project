import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk 
import sqlite3
from database import *

# Δημιουργία παραθύρου
def login():
    username = entry_username.get()
    password = entry_password.get()
    
    role = check_login(username, password)
    if role:
        messagebox.showinfo("Επιτυχία", f"Καλωσήρθες, {role}!")
    else:
        messagebox.showerror("Σφάλμα", "Λάθος όνομα χρήστη ή κωδικός.")
def main_page():
    global bg_photo
    window = tk.Tk()
    window.title("Σύστημα Σύνδεσης")
    window.geometry("800x600")  # Ορισμός μεγέθους παραθύρου

    # Προσθήκη εικόνας φόντου
    bg_image = Image.open("pingpong.webp")  # Η εικόνα που θα χρησιμοποιηθεί ως φόντο
    bg_image = bg_image.resize((800, 600), Image.Resampling.LANCZOS)
    window.resizable(False, False)
    bg_photo = ImageTk.PhotoImage(bg_image)

    bg_label = tk.Label(window, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)  # Ρύθμιση πλήρους φόντου

    # Δημιουργία πλαισίου για τα widgets
    frame = tk.Frame(window, bg="#31363F",relief="solid", padx=30, pady=30,highlightbackground="#222831", highlightthickness=5)
    frame.pack(pady=150)  # Χρήση `pack` για τοποθέτηση

    # Προσθήκη ετικετών και πεδίων εισαγωγής
    tk.Label(frame, text="Όνομα Χρήστη:", bg="#31363F",font=("Arial", 12),fg="white").pack(anchor="w", pady=5)
    global entry_username
    entry_username = tk.Entry(frame, width=30,bd=1)
    entry_username.pack(pady=5)

    tk.Label(frame, text="Κωδικός:", bg="#31363F",font=("Arial", 12),fg="white").pack(anchor="w", pady=5)
    global entry_password
    entry_password = tk.Entry(frame, show="*", width=30,bd=1)
    entry_password.pack(pady=5)

    # Προσθήκη κουμπιού σύνδεσης
  
    tk.Button(frame, text="Σύνδεση", command=login, font=("Arial", 12), bg="#76ABAE", fg="white", 
                       relief="raised", padx=10, pady=5, bd=3, highlightthickness=0).pack(pady=10)
    return window
def main():
    create_database()

    # Δημιουργία παραθύρου με tkinter
    window=main_page()
    window.mainloop()

if __name__ == "__main__":
    main()
