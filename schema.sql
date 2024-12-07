BEGIN TRANSACTION;

-- Δημιουργία πίνακα "ΜΕΛΟΣ"
DROP TABLE IF EXISTS "ΜΕΛΟΣ";
CREATE TABLE IF NOT EXISTS "ΜΕΛΟΣ" (
    "μητρώο_μέλους" CHAR(4) NOT NULL PRIMARY KEY,
    "όνομα" VARCHAR(255) NOT NULL,
    "επώνυμο" VARCHAR(255) NOT NULL,
    "ημερομηνία_γέννησης" DATE CHECK ("ημερομηνία_γέννησης" <= CURRENT_DATE),
    "επίπεδο" VARCHAR(50) CHECK ("επίπεδο" IN ('ΑΡΧΑΡΙΟΣ', 'ΕΡΑΣΙΤΕΧΝΗΣ', 'ΠΡΟΧΩΡΗΜΕΝΟΣ', 'ΕΠΑΓΓΕΛΜΑΤΙΑΣ')),
    "τηλέφωνο" CHAR(10) CHECK ("τηλέφωνο" GLOB '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'),
    "φύλο" VARCHAR(20) CHECK ("φύλο" IN ('ΑΡΡΕΝ', 'ΘΗΛΥ')),
    "πλήθος_αδελφών" INTEGER DEFAULT 0 CHECK ("πλήθος_αδελφών" >= 0),
    CONSTRAINT chk_μητρώο_μέλους CHECK ("μητρώο_μέλους" GLOB '[0-9][0-9][0-9][0-9]')
);

-- Δημιουργία πίνακα "ΠΑΙΚΤΗΣ"
DROP TABLE IF EXISTS "ΠΑΙΚΤΗΣ";
CREATE TABLE IF NOT EXISTS "ΠΑΙΚΤΗΣ" (
    "RN" CHAR(5) NOT NULL, 
    "μητρώο_μέλους" CHAR(4) NOT NULL,
    "Δελτίο_ΑΘλητή" BLOB DEFAULT NULL,  -- Το πεδίο αυτό αποθηκεύει δυαδικά δεδομένα
    PRIMARY KEY ("RN", "μητρώο_μέλους"),
    FOREIGN KEY ("μητρώο_μέλους") REFERENCES "ΜΕΛΟΣ"("μητρώο_μέλους") ON DELETE CASCADE ON UPDATE CASCADE
    CONSTRAINT chk_rn CHECK ("RN" GLOB '[0-9][0-9][0-9][0-9][0-9]')
);
-- Δημιουργία πίνακα "ΞΕΝΟΣ ΠΑΙΚΤΗΣ"
DROP TABLE IF EXISTS "ΞΕΝΟΣ ΠΑΙΚΤΗΣ";
CREATE TABLE IF NOT EXISTS "ΞΕΝΟΣ ΠΑΙΚΤΗΣ" (
    "RN" CHAR(5) NOT NULL,
    "μητρώο_μέλους" CHAR(4),
    "ομάδα" VARCHAR(50) NOT NULL,
    PRIMARY KEY ("RN", "μητρώο_μέλους"),
    FOREIGN KEY ("RN", "μητρώο_μέλους") REFERENCES "ΠΑΙΚΤΗΣ" ("RN", "μητρώο_μέλους") ON DELETE CASCADE ON UPDATE CASCADE
);
-- Δημιουργία πίνακα "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ"
DROP TABLE IF EXISTS "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ";
CREATE TABLE IF NOT EXISTS "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ" (
    "RN" CHAR(5) NOT NULL,
    "μητρώο_μέλους" CHAR(4) NOT NULL,
    "ήττες" INTEGER DEFAULT 0,
    "νίκες" INTEGER DEFAULT 0,
    "points" FLOAT DEFAULT 0,
    "κατηγορία" VARCHAR(50),
    PRIMARY KEY ("RN", "μητρώο_μέλους"),
    FOREIGN KEY ("RN", "μητρώο_μέλους") REFERENCES "ΠΑΙΚΤΗΣ"("RN", "μητρώο_μέλους") ON DELETE CASCADE ON UPDATE CASCADE
 
);
DROP TABLE IF EXISTS "ΑΜΕΙΒΟΜΕΝΟΣ ΠΑΙΚΤΗΣ";
CREATE TABLE IF NOT EXISTS "ΑΜΕΙΒΟΜΕΝΟΣ ΠΑΙΚΤΗΣ" (
    "RN" CHAR(5) NOT NULL,
    "μητρώο_μέλους" CHAR(4) NOT NULL,                                          -- Αριθμός εγγραφής του παίκτη
    "ΑΦΜ" VARCHAR UNIQUE CHECK ("ΑΦΜ" GLOB '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'),                 -- ΑΦΜ (9 ψηφία, μοναδικό)
    "αμοιβή" FLOAT CHECK (αμοιβή >= 0),                                -- Αμοιβή (δεν μπορεί να είναι αρνητική)
    "ημερομηνία έναρξης συμβολαίου" DATE,                              -- Ημερομηνία έναρξης συμβολαίου
    "ημερομηνία λήξης συμβολαίου" DATE,                                -- Ημερομηνία λήξης συμβολαίου
    "IBAN" CHAR(27) UNIQUE CHECK (LENGTH("IBAN") = 27 AND "IBAN" GLOB 'GR[0-9][0-9][0-9A-Z]*'), -- IBAN (26 χαρακτήρες, ξεκινά με GR, μοναδικό)
    PRIMARY KEY ("RN", "μητρώο_μέλους"),  -- Συνθετό πρωτεύον κλειδί με τα πεδία RN και μητρώο_μέλους
    FOREIGN KEY ("RN", "μητρώο_μέλους") REFERENCES "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ" ("RN", "μητρώο_μέλους")
			ON DELETE CASCADE
			ON UPDATE CASCADE
    CHECK ("ημερομηνία έναρξης συμβολαίου" <= "ημερομηνία λήξης συμβολαίου")  -- Ημερομηνία έναρξης <= ημερομηνία λήξης
);

DROP TABLE IF EXISTS "ΠΡΟΣΩΠΙΚΟ";
CREATE TABLE IF NOT EXISTS "ΠΡΟΣΩΠΙΚΟ" (
	"email" VARCHAR CHECK ("email" GLOB '*@*.*'),
	"ΑΦΜ" VARCHAR UNIQUE CHECK ("ΑΦΜ" GLOB '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'),
	"αμοιβή" FLOAT CHECK ("αμοιβή" >= 0),
	"τηλέφωνο" CHAR(10) CHECK ("τηλέφωνο" GLOB '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'),
	"όνομα" varchar,
	"επώνυμο" varchar,
	"IBAN" CHAR(26) UNIQUE CHECK (LENGTH("IBAN") = 27 AND "IBAN" GLOB 'GR[0-9][0-9][0-9A-Z]*'), -- IBAN (26 χαρακτήρες, ξεκινά με GR, μοναδικό)
	PRIMARY KEY ("email")
);
DROP TABLE IF EXISTS "ΓΡΑΜΜΑΤΕΑΣ";
CREATE TABLE IF NOT EXISTS "ΓΡΑΜΜΑΤΕΑΣ" (
	"email" VARCHAR CHECK ("email" GLOB '*@*.*'),
	PRIMARY KEY ("email"),
	FOREIGN KEY ("email") REFERENCES "ΠΡΟΣΩΠΙΚΟ" ("email")
			ON DELETE CASCADE 
			ON UPDATE CASCADE
);

DROP TABLE IF EXISTS "ΠΡΟΠΟΝΗΤΗΣ";
CREATE TABLE IF NOT EXISTS "ΠΡΟΠΟΝΗΤΗΣ" (
	"email" VARCHAR  CHECK ("email" GLOB '*@*.*'),
	PRIMARY KEY ("email"),
	FOREIGN KEY ("email") REFERENCES "ΠΡΟΣΩΠΙΚΟ" ("email")
			ON DELETE CASCADE
			ON UPDATE CASCADE
);
DROP TABLE IF EXISTS "ΜΕΛΟΣ_ΠΛΗΡΩΝΕΙ_ΣΥΝΔΡΟΜΗ";
CREATE TABLE IF NOT EXISTS "ΜΕΛΟΣ_ΠΛΗΡΩΝΕΙ_ΣΥΝΔΡΟΜΗ" (
    "κωδικός συνδρομής" INTEGER DEFAULT 0,
    "μητρώο_μέλους" CHAR(4) NOT NULL, 
    "ημερομηνία πληρωμής" DATE,
    PRIMARY KEY ("κωδικός συνδρομής", "μητρώο_μέλους"),
    FOREIGN KEY ("κωδικός συνδρομής") REFERENCES "ΣΥΝΔΡΟΜΗ" ("κωδικός συνδρομής")
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
    FOREIGN KEY ("μητρώο_μέλους") REFERENCES "ΜΕΛΟΣ" ("μητρώο_μέλους")
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);
DROP TABLE IF EXISTS "ΠΡΟΠΟΝΗΤΗΣ_ΠΡΟΠΟΝΕΙ_ΜΕΛΟΣ";
CREATE TABLE IF NOT EXISTS "ΠΡΟΠΟΝΗΤΗΣ_ΠΡΟΠΟΝΕΙ_ΜΕΛΟΣ" (
    "μητρώο_μέλους" CHAR(4) NOT NULL, 
    "email" VARCHAR DEFAULT NULL CHECK ("email" GLOB '*@*.*'),
    "ημερομηνία προπόνησης" DATE,
    "κατάσταση" VARCHAR CHECK ("κατάσταση" IN ('ΑΠΩΝ/ΟΥΣΑ','ΠΑΡΩΝ/ΟΥΣΑ')),
    FOREIGN KEY ("μητρώο_μέλους") REFERENCES "ΜΕΛΟΣ" ("μητρώο_μέλους")
        ON DELETE SET DEFAULT 
        ON UPDATE CASCADE,
    FOREIGN KEY ("email") REFERENCES "ΠΡΟΣΩΠΙΚΟ" ("email")
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);
DROP TABLE IF EXISTS "ΣΥΝΔΡΟΜΗ";
CREATE TABLE IF NOT EXISTS "ΣΥΝΔΡΟΜΗ" (
    "τρόπος πληρωμής" VARCHAR CHECK ("τρόπος πληρωμής" IN ('Μετρητά','Κάρτα')),
    "πακέτα συνδρομής" VARCHAR CHECK ("πακέτα συνδρομής" IN ('2 αδέλφια', '3 αδέλφια', 'Ξένος Παίκτης', 'Παίκτης της Ομάδας','Κανονικη')),
    "κωδικός συνδρομής" INTEGER PRIMARY KEY
);



INSERT INTO "ΜΕΛΟΣ" ("μητρώο_μέλους", "όνομα", "επώνυμο", "ημερομηνία_γέννησης", "επίπεδο", "τηλέφωνο", "φύλο", "πλήθος_αδελφών")
VALUES
('0001', 'ΑΝΤΩΝΙΑΔΗΣ', 'ΝΙΚΟΛΑΟΣ', '1998-09-25', 'ΕΠΑΓΓΕΛΜΑΤΙΑΣ', '6942229454', 'ΑΡΡΕΝ', 0),
('0002', 'ΚΟΡΔΟΥΤΗΣ', 'ΔΗΜΗΤΡΗΣ', '1999-09-22', 'ΕΠΑΓΓΕΛΜΑΤΙΑΣ', '6901234567', 'ΑΡΡΕΝ', 0),
('0003', 'ΟΡΑΝΤΟΠΟΥΛΟΣ', 'ΔΗΜΗΤΡΙΟΣ', '2001-12-21', 'ΕΠΑΓΓΕΛΜΑΤΙΑΣ', '6932987654', 'ΑΡΡΕΝ', 0),
('0004', 'ΣΙΑΧΟΣ', 'ΝΙΚΟΛΑΟΣ', '1998-07-02', 'ΕΠΑΓΓΕΛΜΑΤΙΑΣ', '6981015405', 'ΑΡΡΕΝ', 0),
('0005', 'ΔΑΣΚΑΛΟΠΟΥΛΟΣ', 'ΑΝΑΣΤΑΣΙΟΣ', '1970-07-05', 'ΠΡΟΧΩΡΗΜΕΝΟΣ', '6977072037', 'ΑΡΡΕΝ', 0),
('0006', 'ΓΕΩΡΓΙΟΥ', 'ΔΗΜΗΤΡΙΟΣ', '2002-09-09', 'ΠΡΟΧΩΡΗΜΕΝΟΣ', '6947690015', 'ΑΡΡΕΝ', 0),
('0007', 'ΤΣΑΚΑΛΗΣ', 'ΣΠΥΡΙΔΩΝ-ΜΑΡΙΟΣ', '2011-03-02', 'ΕΡΑΣΙΤΕΧΝΗΣ', '6939893576', 'ΑΡΡΕΝ', 0),
('0008', 'ΘΕΟΔΩΡΟΠΟΥΛΟΣ', 'ΟΡΕΣΤΗΣ', '2012-11-28', 'ΕΡΑΣΙΤΕΧΝΗΣ', '6978690644', 'ΑΡΡΕΝ', 1),
('0009', 'ΓΚΟΝΤΕΒΑΣ', 'ΓΕΩΡΓΙΟΣ', '2003-04-20', 'ΕΡΑΣΙΤΕΧΝΗΣ', '6945678901', 'ΑΡΡΕΝ', 0),
('0010', 'ΣΠΑΝΟΣ', 'ΑΓΓΕΛΟΣ-ΚΩΝΣΤΑΝΤΙΝΟΣ', '2010-05-18', 'ΕΡΑΣΙΤΕΧΝΗΣ', '6971628175', 'ΑΡΡΕΝ', 0),
('0011', 'ΚΟΤΣΙΦΑΣ', 'ΠΑΝΑΓΙΩΤΗΣ', '2010-04-13', 'ΕΡΑΣΙΤΕΧΝΗΣ', '6988184773', 'ΑΡΡΕΝ', 0),
('0012', 'ΘΕΟΔΩΡΟΠΟΥΛΟΥ', 'ΚΩΝΣΤΑΝΤΙΝΑ', '2008-03-22', 'ΠΡΟΧΩΡΗΜΕΝΟΣ', '6977123456', 'ΘΗΛΥ', 1),
('0013', 'ΦΙΛΟΠΟΥΛΟΥ', 'ΚΩΝΣΤΑΝΤΙΝΑ', '2012-02-11', 'ΕΡΑΣΙΤΕΧΝΗΣ', '6974110687', 'ΘΗΛΥ', 0),
('0014', 'ΚΑΤΣΟΥΛΗ', 'ΑΓΓΕΛΙΝΑ', '2009-06-12', 'ΠΡΟΧΩΡΗΜΕΝΟΣ', '6945125957', 'ΘΗΛΥ', 0),
('0015', 'ΛΑΙΖΗΝΟΥ', 'ΧΡΙΣΤΙΝΑ', '2013-08-22', 'ΕΡΑΣΙΤΕΧΝΗΣ', '6937349585', 'ΘΗΛΥ', 0),
('0016', 'ΤΣΙΩΤΟΣ', 'ΧΡΗΣΤΟΣ', '2009-02-14', 'ΠΡΟΧΩΡΗΜΕΝΟΣ', '6945585175', 'ΑΡΡΕΝ', 0),
('0017', 'ΓΡΟΥΜΠΟΣ', 'ΓΙΩΡΓΗΣ', '2005-03-11', 'ΕΡΑΣΙΤΕΧΝΗΣ', '6993013282', 'ΑΡΡΕΝ', 0),
('0018', 'ΠΟΛΥΧΡΟΝΙΑΔΗΣ', 'ΒΑΓΓΕΛΗΣ', '2013-01-03', 'ΑΡΧΑΡΙΟΣ', '6972002275', 'ΑΡΡΕΝ', 0),
('0019', 'ΖΑΡΡΟΣ', 'ΑΝΔΡΕΑΣ', '1966-04-04', 'ΕΡΑΣΙΤΕΧΝΗΣ', '6976194964', 'ΑΡΡΕΝ', 0),
('0020', 'ΔΗΜΟΠΟΥΛΟΥ', 'ΔΩΡΑ', '2015-01-30', 'ΑΡΧΑΡΙΟΣ', '6978395017', 'ΘΗΛΥ', 2),
('0021', 'ΔΗΜΟΠΟΥΛΟΥ', 'ΚΩΝΣΤΑΝΤΙΝΑ', '2016-03-03', 'ΑΡΧΑΡΙΟΣ', '6978395017', 'ΘΗΛΥ', 2),
('0022', 'ΔΗΜΟΠΟΥΛΟΥ', 'ΠΟΛΥΞΕΝΗ', '2016-03-03', 'ΑΡΧΑΡΙΟΣ', '6978395017', 'ΘΗΛΥ', 2),
('0023', 'ΖΑΡΚΟΣ', 'ΠΑΝΑΓΙΩΤΗΣ', '2016-06-05', 'ΑΡΧΑΡΙΟΣ', '6949662866', 'ΑΡΡΕΝ', 0),
('0024', 'ΚΟΛΙΜΑΔΗ', 'ΕΜΜΑΝΟΥΕΛΑ', '2016-08-07', 'ΑΡΧΑΡΙΟΣ', '6944561126', 'ΘΗΛΥ', 0),
('0025', 'ΣΚΑΦΙΔΑ', 'ΜΑΡΙΖΑ', '2015-07-18', 'ΑΡΧΑΡΙΟΣ', '6932587685', 'ΘΗΛΥ', 0),
('0026', 'ΝΤΡΕΤΣΑ', 'ΕΝΤΙ', '2015-08-18', 'ΑΡΧΑΡΙΟΣ', '6994476053', 'ΑΡΡΕΝ', 0),
('0027', 'ΦΛΑΣΚΗΣ', 'ΒΑΣΙΛΗΣ', '2013-08-03', 'ΑΡΧΑΡΙΟΣ', '6981098200', 'ΑΡΡΕΝ', 0),
('0028', 'ΝΤΟΙ', 'ΑΜΕΛΝΤΑ', '2013-05-07', 'ΑΡΧΑΡΙΟΣ', '6994800250', 'ΘΗΛΥ', 0),
('0029', 'ΣΟΥΛΑ', 'ΑΝΤΩΝΙΟΣ', '2002-06-18', 'ΠΡΟΧΩΡΗΜΕΝΟΣ', '6996306216', 'ΑΡΡΕΝ', 0),
('0030', 'ΤΣΕΠΗΣ', 'ΜΙΛΤΙΑΔΗΣ', '2008-05-13', 'ΠΡΟΧΩΡΗΜΕΝΟΣ', '6980338496', 'ΑΡΡΕΝ', 0),
('0031', 'ΞΟΥΡΙΔΑΣ', 'ΙΩΑΝΝΗΣ', '1990-11-19', 'ΠΡΟΧΩΡΗΜΕΝΟΣ', '6976194964', 'ΑΡΡΕΝ', 0);
INSERT INTO "ΠΑΙΚΤΗΣ" ("μητρώο_μέλους", "RN")
VALUES
('0001', '20663'),
('0002', '21252'),
('0003', '28048'),
('0004', '21400'),
('0005', '07916'),
('0006', '24448'),
('0007', '27712'),
('0008', '27713'),
('0009', '24432'),
('0010', '27696'),
('0011', '27698'),
('0012', '26069'),
('0013', '27697'),
('0014', '27248'),
('0015', '27919'),
('0016', '26665'),
('0019', '08032'),
('0029', '24446'),
('0030', '27136'),
('0031', '19938');
INSERT INTO "ΞΕΝΟΣ ΠΑΙΚΤΗΣ" ("μητρώο_μέλους", "RN", "ομάδα")
VALUES
('0016', '26665', 'ΑΟ ΔΙΟΓΕΝΗΣ ΠΑΤΡΑΣ'),
('0019', '08032', 'ΑΟ ΦΟΙΝΙΚΑΣ ΠΑΤΡΩΝ 2010'),
('0029', '24446', 'ΑΟ ΠΑΤΡΑΣ ΠΑΓΩΝΑ'),
('0030', '27136', 'ΑΟ ΔΙΟΓΕΝΗΣ ΠΑΤΡΑΣ'),
('0031', '19938', 'ΑΟ ΦΟΙΝΙΚΑΣ ΠΑΤΡΩΝ 2010');

INSERT INTO "ΠΑΙΚΤΗΣ ΤΗΣ ΟΜΑΔΑΣ"("μητρώο_μέλους","RN","ήττες","νίκες","points")
VALUES
('0001','20663',2,5,2395),
('0002','21252',2,4,2362),
('0003','28048',2,4,2157.1),
('0004','21400',4,1,1567.6),
('0005','07916',0,0,1093.7),
('0006','24448',4,0,520.8),
('0007','27712',0,2,269.2),
('0008','27713',0,2,239.6),
('0009','24432',0,0,200),
('0010','27696',0,1,196.3),
('0011','27698',0,3,174.8),
('0012','26069',3,1,458.5),
('0013','27697',1,2,386.6),
('0014','27248',3,2,260.5),
('0015','27919',1,3,258.6);
INSERT INTO "ΑΜΕΙΒΟΜΕΝΟΣ ΠΑΙΚΤΗΣ" ("RN", "μητρώο_μέλους", "ΑΦΜ", "αμοιβή", "ημερομηνία έναρξης συμβολαίου", "ημερομηνία λήξης συμβολαίου", "IBAN")
VALUES
('20663', '0001', '123532654', 5000, '2024-08-15', '2026-08-15', 'GR2101234567890123456789012'),
('21252', '0002', '542871639', 3000, '2024-08-15', '2025-08-15', 'GR3502345678901234567890123'),
('28048', '0003', '108734256', 2000, '2023-09-12', '2027-09-12', 'GR4703456789012345678901234'),
('21400', '0004', '451892637', 1000, '2022-09-06', '2027-09-06', 'GR6305678901234567890123456');

INSERT INTO "ΠΡΟΣΩΠΙΚΟ" ("email", "ΑΦΜ", "αμοιβή", "τηλέφωνο", "όνομα", "επώνυμο", "IBAN")
VALUES
('soula.antonios@gmail.com', '151709432', 500, '6996306216', 'ΑΝΤΩΝΙΟΣ', 'ΣΟΥΛΑ', 'GR5604567890123456789012345'),
('g.xouridas@gmail.com', '104114335', 500, '6976194964', 'ΙΩΑΝΝΗΣ', 'ΞΟΥΡΙΔΑΣ', 'GR4801725070005507060762258'),
('tziantopoulos@gmail.com', '103223493', 350, '6983456789', 'ΣΤΑΜΑΤΗΣ', 'ΤΖΙΑΝΤΟΠΟΥΛΟΣ', 'GR1601101234567890123456789');
-- Εισαγωγή ΓΡΑΜΜΑΤΕΑΣ
INSERT INTO "ΓΡΑΜΜΑΤΕΑΣ" ("email") 
VALUES ('tziantopoulos@gmail.com');

-- Εισαγωγή ΠΡΟΠΟΝΗΤΗΣ
INSERT INTO "ΠΡΟΠΟΝΗΤΗΣ" ("email") 
VALUES ('soula.antonios@gmail.com'), 
       ('g.xouridas@gmail.com');
INSERT INTO "ΣΥΝΔΡΟΜΗ" ("τρόπος πληρωμής", "πακέτα συνδρομής", "κωδικός συνδρομής") 
VALUES
('Μετρητά', '2 αδέλφια', 1),
('Μετρητά', '3 αδέλφια', 2),
('Μετρητά', 'Ξένος Παίκτης', 3),
('Μετρητά', 'Παίκτης της Ομάδας', 4),
('Μετρητά', 'Κανονικη', 5),
('Κάρτα', '2 αδέλφια', 6),
('Κάρτα', '3 αδέλφια', 7),
('Κάρτα', 'Ξένος Παίκτης', 8),
('Κάρτα', 'Παίκτης της Ομάδας', 9),
('Κάρτα', 'Κανονικη', 10);


COMMIT;

