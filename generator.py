# Re-import necessary libraries and re-define the function to continue execution after the reset.
import sqlite3
import random
from datetime import datetime, timedelta
from collections import defaultdict

# Original lists
emails = ['soula.antonios@gmail.com', 'g.xouridas@gmail.com']
member_ids = ['0001', '0002', '0003', '0004', '0005', '0006', '0007', '0008', '0009', '0010',
              '0011', '0012', '0013', '0014', '0015', '0016', '0017', '0018', '0019', '0020',
              '0021', '0022', '0023', '0024', '0025', '0026', '0027', '0028', '0029', '0030', '0031']
statuses = ['ΠΑΡΩΝ/ΟΥΣΑ', 'ΑΠΩΝ/ΟΥΣΑ']
# Generate weekdays function
def generate_weekdays(start_date, end_date):
    current_date = start_date
    weekdays = []
    while current_date <= end_date:
        if current_date.weekday() < 5:  # Monday to Friday
            weekdays.append(current_date)
        current_date += timedelta(days=1)
    return weekdays

# Date range for presences
start_date = datetime(2024, 9, 1)
end_date = datetime(2024, 12, 23)

# Generate the weekdays list
weekdays = generate_weekdays(start_date, end_date)

# Function to create assignments with weekly limits
def create_limited_assignments(emails, member_ids, weekdays, num_assignments, max_per_week):
    assignments = []
    used_combinations = set()  # Set to track used combinations
    weekly_usage = defaultdict(lambda: defaultdict(int))  # Track usage by member and week

    for _ in range(num_assignments):
        email = random.choice(emails)
        member = random.choice(member_ids)
        state=random.choice(statuses)
        # Keep picking until we find a valid date
        date = random.choice(weekdays)
        week_number = date.isocalendar()[1]

        combination = (email, member, date)
        while (combination in used_combinations or 
               weekly_usage[member][week_number] >= max_per_week or (email=='soula.antonios@gmail.com' and member=='0029') or (email=='g.xouridas@gmail.com' and member=='0031')):
            member = random.choice(member_ids)
            date = random.choice(weekdays)
            week_number = date.isocalendar()[1]
            combination = (email, member, date)

        # Add valid assignment to the list and update tracking
        
        assignments.append((email, member, date,state))
        used_combinations.add(combination)
        weekly_usage[member][week_number] += 1

    return assignments

# Constants for the new rules
num_assignments = 500  # Number of records to generate
max_per_week = 3  # Maximum 3 dates per week per member

# Generate assignments with the new rule
assignments_limited = create_limited_assignments(emails, member_ids, weekdays, num_assignments, max_per_week)

# Format assignments to save them in a text file
assignments_text_limited = "\n".join([
    f'("{assignment[1]}","{assignment[0]}","{assignment[2].strftime("%Y-%m-%d")}","{assignment[3]}"),'
    for assignment in assignments_limited
])

# Save to file
file_path_limited = 'assignments.txt'
with open(file_path_limited, 'w') as file:
    file.write(assignments_text_limited)

conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS "ΠΡΟΠΟΝΗΤΗΣ_ΠΡΟΠΟΝΕΙ_ΜΕΛΟΣ" (
    "μητρώο_μέλους" CHAR(4) NOT NULL,
    "email" VARCHAR DEFAULT NULL CHECK ("email" GLOB '*@*.*'),
    "ημερομηνία προπόνησης" DATE,
    "κατάσταση" VARCHAR CHECK ("κατάσταση" IN ('ΑΠΩΝ/ΟΥΣΑ','ΠΑΡΩΝ/ΟΥΣΑ')),
    FOREIGN KEY ("μητρώο_μέλους") REFERENCES "ΜΕΛΟΣ" ("μητρώο_μέλους"),
    FOREIGN KEY ("email") REFERENCES "ΠΑΙΚΤΗΣ" ("email")
);
""")
for assignment in assignments_limited:
    member_id = assignment[1]
    email = assignment[0]
    date = assignment[2].strftime("%Y-%m-%d")
    state = assignment[3]

    cursor.execute("""
    INSERT INTO "ΠΡΟΠΟΝΗΤΗΣ_ΠΡΟΠΟΝΕΙ_ΜΕΛΟΣ" ("μητρώο_μέλους", "email", "ημερομηνία προπόνησης", "κατάσταση")
    VALUES (?, ?, ?, ?)
    """, (member_id, email, date, state))

# Επιβεβαίωση και αποθήκευση
conn.commit()

# Κλείσιμο της σύνδεσης
conn.close()