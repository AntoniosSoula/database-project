import sqlite3
# Δημιουργία/Σύνδεση με βάση δεδομένων
def create_database():
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

# Συνάρτηση για τον έλεγχο των στοιχείων σύνδεσης
def check_login(username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username = ? AND password = ?", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# Συνάρτηση για το κουμπί "Σύνδεση"
