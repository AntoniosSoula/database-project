import sqlite3
import random
import sqlite3
def check_member_in_another_team(member_id):
    # Σύνδεση με τη βάση δεδομένων
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Ερώτημα για να ελέγξουμε αν το μητρωο_μελους υπάρχει στους ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ
    cursor.execute("""
        SELECT 1 FROM "ΞΕΝΟΣ ΠΑΙΚΤΗΣ"
        WHERE "μητρώο_μέλους" = ?
        LIMIT 1
    """, (member_id,))
    
    # Αν βρεθεί το μέλος στον πίνακα, η ερώτηση θα επιστρέψει μια εγγραφή
    result = cursor.fetchone()
    
    # Κλείσιμο της σύνδεσης με τη βάση δεδομένων
    conn.close()

    # Επιστροφή True αν το μέλος υπάρχει, αλλιώς False
    return result is not None

# Συνάρτηση για να ελέγξουμε αν το μέλος υπάρχει στους 'ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ'
def check_member_in_team(member_id):
    # Σύνδεση με τη βάση δεδομένων
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Ερώτημα για να ελέγξουμε αν το μητρωο_μελους υπάρχει στους ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ
    cursor.execute("""
        SELECT 1 FROM "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ"
        WHERE "μητρώο_μέλους" = ?
        LIMIT 1
    """, (member_id,))
    
    # Αν βρεθεί το μέλος στον πίνακα, η ερώτηση θα επιστρέψει μια εγγραφή
    result = cursor.fetchone()
    
    # Κλείσιμο της σύνδεσης με τη βάση δεδομένων
    conn.close()

    # Επιστροφή True αν το μέλος υπάρχει, αλλιώς False
    return result is not None

# Συνάρτηση για να συνδεθούμε στη βάση δεδομένων και να εκτελέσουμε τα ερωτήματα
def get_players_data():
    # Σύνδεση με την βάση δεδομένων
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Ερώτημα για να πάρουμε όλα τα δεδομένα από τον πίνακα συνδρομη
    cursor.execute("""SELECT * FROM "ΣΥΝΔΡΟΜΗ" """)
    subscription_data = cursor.fetchall()
    
    # Ερώτημα για να πάρουμε τα δεδομένα των μελών που δεν ανήκουν στους 'ΑΜΕΙΒΟΜΕΝΟΥΣ'
    cursor.execute("""
        SELECT * FROM "ΜΕΛΟΣ"
        WHERE "μητρώο_μέλους" NOT IN (
            SELECT "μητρώο_μέλους" FROM "ΑΜΕΙΒΟΜΕΝΟΣ ΠΑΙΚΤΗΣ"
        )
    """)
    members_data = cursor.fetchall()
    
    # Κλείσιμο της σύνδεσης με την βάση δεδομένων
    conn.close()

    # Επιστροφή των δεδομένων
    return subscription_data, members_data
def match_members_with_subcriptions(subscriptions,members):
    member_subscription=[]
    for member in members:
        if check_member_in_team(member[0]):
            options=[4,9]
        elif check_member_in_another_team(member[0]):
            options=[3,8]
        elif member[-1]==1:
            options=[1,6]
        elif member[-1]==2:
            options=[2,7]
        else:
            options=[5,10]
        option=random.choice(options)
        member_subscription.append([option,member[0]])
    return member_subscription
def melos_plironei_sindromi_generator(matching_table, num):
    member_pays_subscription = []
    months = ('09', '10', '11', '12')
    year = 2024  # Προκαθορισμένο έτος
    match_counts = {}  # Λεξικό για να παρακολουθεί πόσες φορές χρησιμοποιείται κάθε match

    for i in range(num):
        match = random.choice(matching_table)
        member = match[1]
        subscription = match[0]

        # Δημιουργία μοναδικού κλειδιού για το match
        match_key = (member, subscription)
        if match_key in match_counts:
            # Αν το match έχει ήδη χρησιμοποιηθεί 4 φορές, παρακάμπτεται
            if match_counts[match_key] >= 4:
                continue
            match_counts[match_key] += 1
        else:
            match_counts[match_key] = 1

        # Μέτρηση πόσες φορές έχει χρησιμοποιηθεί το μέλος
        count = sum(1 for sublist in member_pays_subscription if member == sublist[0])

        # Ασφάλεια για τον αριθμό των μηνών
        if count < len(months):
            month = months[count]
        else:
            month = random.choice(months)  # Αν ξεπεραστούν οι μήνες, επιλέγουμε τυχαία

        # Προσθήκη του έτους μαζί με τον μήνα
        month_year = f"{month}-{year}"

        member_pays_subscription.append([member, subscription, month_year])

    return member_pays_subscription

def insert_matches_into_database(matches):
    # Σύνδεση με τη βάση δεδομένων
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Εισαγωγή των δεδομένων στον πίνακα 'ΜΕΛΟΣ ΠΛΗΡΩΝΕΙ ΣΥΝΔΡΟΜΗ'
    for match in matches:
        member_id, subscription_id, month = match
        cursor.execute("""
            INSERT INTO "ΜΕΛΟΣ_ΠΛΗΡΩΝΕΙ_ΣΥΝΔΡΟΜΗ" ("μητρώο_μέλους", "κωδικός συνδρομής", "ημερομηνία πληρωμής")
            VALUES (?, ?, ?)
        """, (member_id, subscription_id, month))
    
    # Επιβεβαίωση αλλαγών και κλείσιμο σύνδεσης
    conn.commit()
    conn.close()

def main():
    # Απόκτηση δεδομένων συνδρομών και μελών
    subscription_data, members_data = get_players_data()
    
    # Δημιουργία αντιστοιχίσεων μελών-συνδρομών
    member_subcscription = match_members_with_subcriptions(subscription_data, members_data)
    print(member_subcscription)
    
    # Γενιά πληρωμών μελών-συνδρομών
    matches = melos_plironei_sindromi_generator(member_subcscription, 70)
    for match in matches:
        print(match)
        print("\n")
    
    # Εισαγωγή δεδομένων στη βάση
    insert_matches_into_database(matches)

if __name__ == "__main__":
    main()
       
            
            
            
            
            
            

def main():
    subscription_data, members_data = get_players_data()
    member_subcscription=match_members_with_subcriptions(subscription_data,members_data)
    print(member_subcscription)
    matches=melos_plironei_sindromi_generator(member_subcscription,70)
    for match in matches:
        print(match)
        print("\n")


if __name__=="__main__":
    main()