import random
from datetime import datetime, timedelta

# Λίστες με τα email και τα μητρώα μέλους
emails = ['soula.antonios@gmail.com', 'g.xouridas@gmail.com']
member_ids = ['0001', '0002', '0003', '0004', '0005', '0006', '0007', '0008', '0009', '0010',
              '0011', '0012', '0013', '0014', '0015', '0016', '0017', '0018', '0019', '0020',
              '0021', '0022', '0023', '0024', '0025', '0026', '0027', '0028', '0029', '0030', '0031']

# Λίστα ημερομηνιών που δεν περιλαμβάνουν Σαββατοκύριακα
def generate_weekdays(start_date, end_date):
    current_date = start_date
    weekdays = []
    while current_date <= end_date:
        if current_date.weekday() < 5:  # 0: Δευτέρα, 4: Παρασκευή
            weekdays.append(current_date)
        current_date += timedelta(days=1)
    return weekdays

# Ορίστε την ημερομηνία έναρξης και λήξης για τις παρουσίες
start_date = datetime(2024, 9, 1)
end_date = datetime(2024, 12, 23)

# Δημιουργία λίστας εργάσιμων ημερών
weekdays = generate_weekdays(start_date, end_date)

# Λειτουργία για τη δημιουργία τυχαίων συνδυασμών
def create_random_assignments(emails, member_ids, weekdays, num_assignments):
    assignments = []
    used_combinations = set()  # Set to track used combinations

    # Creating records according to the specified number
    for _ in range(num_assignments):
        email = random.choice(emails)

        member = random.choice(member_ids)

        # Choose a random date not already used by this member
        date = random.choice(weekdays)

        # Creating the presence record
        combination = (email, member, date)

        # If the combination exists, skip and retry
        while combination in used_combinations:
            member = random.choice(member_ids)
            date = random.choice(weekdays)
            combination = (email, member, date)

        # Add the combination to the list and set
        assignments.append((email, member, date))
        used_combinations.add(combination)

    return assignments


# Καθορίζουμε πόσες εγγραφές θέλουμε (π.χ. 50 εγγραφές)
num_assignments = 500

# Δημιουργία των τυχαίων συνδυασμών
assignments = create_random_assignments(emails, member_ids, weekdays, num_assignments)

# Save assignments to a text file
assignments_text = "\n".join([f'("{assignment[1]}","{assignment[0]}","{assignment[2].strftime('%Y-%m-%d')}"),' for assignment in assignments])

# Write the assignments to a text file
file_path = 'assignments.txt'
with open(file_path, 'w') as file:
    file.write(assignments_text)

file_path