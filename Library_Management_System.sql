create database Library;
use Library;

DROP TABLE IF EXISTS TRANSACTIONS;
DROP TABLE IF EXISTS BORROWS;
DROP TABLE IF EXISTS AUTH_CREDENTIALS;
DROP TABLE IF EXISTS WRITES;
DROP TABLE IF EXISTS PUBLISHES;
DROP TABLE IF EXISTS MANAGES;
DROP TABLE IF EXISTS READERS;
DROP TABLE IF EXISTS STAFF;
DROP TABLE IF EXISTS BOOKS;
DROP TABLE IF EXISTS AUTHORS;
DROP TABLE IF EXISTS PUBLISHERS;


CREATE TABLE READERS (
    User_ID VARCHAR(10) PRIMARY KEY,
    First_Name VARCHAR(50) NOT NULL,
    Last_Name VARCHAR(50) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    Address VARCHAR(200),
    Phone_Number VARCHAR(15) UNIQUE,
    Registration_Date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_reader_email CHECK (Email LIKE '%@%')
);

select * from READERS;


CREATE TABLE AUTHORS (
    Author_ID VARCHAR(10) PRIMARY KEY,
    First_Name VARCHAR(50) NOT NULL,
    Last_Name VARCHAR(50) NOT NULL,
    Biography TEXT
);

select * from AUTHORS;


CREATE TABLE PUBLISHERS (
    Publisher_ID VARCHAR(10) PRIMARY KEY,
    Publisher_Name VARCHAR(100) NOT NULL UNIQUE,
    Address VARCHAR(200),
    Contact_Email VARCHAR(100),
    CONSTRAINT chk_publisher_email CHECK (Contact_Email LIKE '%@%')
);

SELECT * FROM PUBLISHERS;

CREATE TABLE BOOKS (
    Book_ID VARCHAR(10) PRIMARY KEY,
    Title VARCHAR(200) NOT NULL,
    ISBN VARCHAR(20) UNIQUE NOT NULL,
    Genre VARCHAR(50),
    Edition VARCHAR(20),
    Price DECIMAL(10, 2) CHECK (Price >= 0),
    Total_Copies INT NOT NULL CHECK (Total_Copies >= 0),
    Copies_Available INT NOT NULL CHECK (Copies_Available >= 0),
    CONSTRAINT chk_copies CHECK (Copies_Available <= Total_Copies)
);

SELECT * FROM BOOKS;


CREATE TABLE STAFF (
    Staff_ID VARCHAR(10) PRIMARY KEY,
    First_Name VARCHAR(50) NOT NULL,
    Last_Name VARCHAR(50) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    Position VARCHAR(50) NOT NULL,
    CONSTRAINT chk_staff_email CHECK (Email LIKE '%@%')
);

SELECT * FROM STAFF;

-- AUTH_CREDENTIALS Table (1:1 with STAFF)
CREATE TABLE AUTH_CREDENTIALS (
    Staff_ID VARCHAR(10) NOT NULL,
    Login_ID VARCHAR(20) NOT NULL,
    Password VARCHAR(255) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    PRIMARY KEY (Staff_ID, Login_ID),
    FOREIGN KEY (Staff_ID) REFERENCES STAFF(Staff_ID) ON DELETE CASCADE,
    CONSTRAINT chk_auth_email CHECK (Email LIKE '%@%')
);

SELECT * FROM AUTH_CREDENTIALS;


CREATE TABLE TRANSACTIONS (
    Transaction_ID VARCHAR(10) PRIMARY KEY,
    User_ID VARCHAR(10) NOT NULL,
    Book_ID VARCHAR(10) NOT NULL,
    Borrow_Date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Due_Date DATE NOT NULL,
    Return_Date DATE,
    Status VARCHAR(20) NOT NULL DEFAULT 'Active',
    Fine_Amount DECIMAL(10, 2) DEFAULT 0 CHECK (Fine_Amount >= 0),
    FOREIGN KEY (User_ID) REFERENCES READERS(User_ID) ON DELETE CASCADE,
    FOREIGN KEY (Book_ID) REFERENCES BOOKS(Book_ID) ON DELETE CASCADE,
    CONSTRAINT chk_dates CHECK (Due_Date >= DATE(Borrow_Date)),
    CONSTRAINT chk_return CHECK (Return_Date IS NULL OR Return_Date >= DATE(Borrow_Date)),
    CONSTRAINT chk_status CHECK (Status IN ('Active', 'Returned', 'Overdue', 'Lost'))
);

SELECT * FROM TRANSACTIONS;


CREATE TABLE WRITES (
    Author_ID VARCHAR(10),
    Book_ID VARCHAR(10),
    Author_Role VARCHAR(50) DEFAULT 'Author',
    PRIMARY KEY (Author_ID, Book_ID),
    FOREIGN KEY (Author_ID) REFERENCES AUTHORS(Author_ID) ON DELETE CASCADE,
    FOREIGN KEY (Book_ID) REFERENCES BOOKS(Book_ID) ON DELETE CASCADE
);

SELECT * FROM WRITES;


CREATE TABLE PUBLISHES (
    Publisher_ID VARCHAR(10),
    Book_ID VARCHAR(10),
    Publication_Year INT NOT NULL,
    PRIMARY KEY (Publisher_ID, Book_ID),
    FOREIGN KEY (Publisher_ID) REFERENCES PUBLISHERS(Publisher_ID) ON DELETE CASCADE,
    FOREIGN KEY (Book_ID) REFERENCES BOOKS(Book_ID) ON DELETE CASCADE,
   CONSTRAINT chk_year CHECK (Publication_Year BETWEEN 1000 AND 2100)
);

SELECT * FROM PUBLISHES;


CREATE TABLE MANAGES (
    Staff_ID VARCHAR(10),
    Book_ID VARCHAR(10),
    PRIMARY KEY (Staff_ID, Book_ID),
    FOREIGN KEY (Staff_ID) REFERENCES STAFF(Staff_ID) ON DELETE CASCADE,
    FOREIGN KEY (Book_ID) REFERENCES BOOKS(Book_ID) ON DELETE CASCADE
);

SELECT * FROM MANAGES;


CREATE TABLE BORROWS (
    User_ID VARCHAR(10),
    Book_ID VARCHAR(10),
    Date_Authorized DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (User_ID, Book_ID),
    FOREIGN KEY (User_ID) REFERENCES READERS(User_ID) ON DELETE CASCADE,
    FOREIGN KEY (Book_ID) REFERENCES BOOKS(Book_ID) ON DELETE CASCADE
);

SELECT * FROM BORROWS;


INSERT INTO READERS (User_ID, First_Name, Last_Name, Email, Address, Phone_Number, Registration_Date)
VALUES 
    ('R001', 'John', 'Smith', 'john.smith@email.com', '123 Main St, City', '1234567890', '2024-01-15'),
    ('R002', 'Mary', 'Johnson', 'mary.j@email.com', '456 Oak Ave, Town', '2345678901', '2024-02-20'),
    ('R003', 'Robert', 'Williams', 'rob.will@email.com', '789 Pine Rd, Village', '3456789012', '2024-03-10'),
    ('R004', 'Sarah', 'Brown', 'sarah.b@email.com', '321 Elm St, City', '4567890123', '2024-04-05'),
    ('R005', 'Michael', 'Davis', 'mike.d@email.com', '654 Maple Dr, Town', '5678901234', '2024-05-12');


INSERT INTO AUTHORS (Author_ID, First_Name, Last_Name, Biography)
VALUES 
    ('A001', 'George', 'Orwell', 'English novelist and essayist, best known for 1984 and Animal Farm'),
    ('A002', 'Jane', 'Austen', 'English novelist known for Pride and Prejudice'),
    ('A003', 'Mark', 'Twain', 'American writer and humorist'),
    ('A004', 'Agatha', 'Christie', 'English writer known for detective novels'),
    ('A005', 'J.K.', 'Rowling', 'British author of the Harry Potter series');


INSERT INTO PUBLISHERS (Publisher_ID, Publisher_Name, Address, Contact_Email)
VALUES 
    ('P001', 'Penguin Books', '80 Strand, London', 'contact@penguin.com'),
    ('P002', 'HarperCollins', '195 Broadway, New York', 'info@harpercollins.com'),
    ('P003', 'Random House', '1745 Broadway, New York', 'contact@randomhouse.com'),
    ('P004', 'Scholastic', '557 Broadway, New York', 'info@scholastic.com'),
    ('P005', 'Oxford University Press', 'Great Clarendon St, Oxford', 'contact@oup.com');


INSERT INTO BOOKS (Book_ID, Title, ISBN, Genre, Edition, Price, Total_Copies, Copies_Available)
VALUES 
    ('B001', '1984', '978-0451524935', 'Dystopian', '1st', 15.99, 5, 3),
    ('B002', 'Pride and Prejudice', '978-0141439518', 'Romance', '2nd', 12.99, 4, 4),
    ('B003', 'Adventures of Huckleberry Finn', '978-0486280615', 'Adventure', '1st', 10.99, 3, 2),
    ('B004', 'Murder on the Orient Express', '978-0062693662', 'Mystery', '1st', 14.99, 6, 5),
    ('B005', 'Harry Potter and the Sorcerer Stone', '978-0439708180', 'Fantasy', '1st', 19.99, 8, 6),
    ('B006', 'Animal Farm', '978-0451526342', 'Political Fiction', '1st', 13.99, 4, 3),
    ('B007', 'Emma', '978-0141439587', 'Romance', '1st', 11.99, 3, 3),
    ('B008', 'The Adventures of Tom Sawyer', '978-0486400778', 'Adventure', '1st', 9.99, 2, 1);


INSERT INTO STAFF (Staff_ID, First_Name, Last_Name, Email, Position)
VALUES 
    ('S001', 'Alice', 'Wilson', 'alice.wilson@library.com', 'Head Librarian'),
    ('S002', 'Bob', 'Martinez', 'bob.martinez@library.com', 'Assistant Librarian'),
    ('S003', 'Carol', 'Anderson', 'carol.anderson@library.com', 'Library Assistant'),
    ('S004', 'David', 'Thomas', 'david.thomas@library.com', 'Cataloger'),
    ('S005', 'Emma', 'Garcia', 'emma.garcia@library.com', 'Reference Librarian');


INSERT INTO AUTH_CREDENTIALS (Login_ID, Staff_ID, Password, Email)
VALUES 
    ('alice_w', 'S001', 'hashed_password_1', 'alice.wilson@library.com'),
    ('bob_m', 'S002', 'hashed_password_2', 'bob.martinez@library.com'),
    ('carol_a', 'S003', 'hashed_password_3', 'carol.anderson@library.com'),
    ('david_t', 'S004', 'hashed_password_4', 'david.thomas@library.com'),
    ('emma_g', 'S005', 'hashed_password_5', 'emma.garcia@library.com');


INSERT INTO WRITES (Author_ID, Book_ID, Author_Role)
VALUES 
    ('A001', 'B001', 'Author'),
    ('A001', 'B006', 'Author'),
    ('A002', 'B002', 'Author'),
    ('A002', 'B007', 'Author'),
    ('A003', 'B003', 'Author'),
    ('A003', 'B008', 'Author'),
    ('A004', 'B004', 'Author'),
    ('A005', 'B005', 'Author');


INSERT INTO PUBLISHES (Publisher_ID, Book_ID, Publication_Year)
VALUES 
    ('P001', 'B001', 1949),
    ('P001', 'B002', 1813),
    ('P002', 'B003', 1884),
    ('P002', 'B004', 1934),
    ('P004', 'B005', 1997),
    ('P001', 'B006', 1945),
    ('P001', 'B007', 1815),
    ('P002', 'B008', 1876);


INSERT INTO MANAGES (Staff_ID, Book_ID)
VALUES 
    ('S001', 'B001'),
    ('S001', 'B002'),
    ('S002', 'B003'),
    ('S002', 'B004'),
    ('S003', 'B005'),
    ('S003', 'B006'),
    ('S004', 'B007'),
    ('S005', 'B008');


INSERT INTO BORROWS (User_ID, Book_ID, Date_Authorized)
VALUES 
    ('R001', 'B001', '2024-01-20'),
    ('R001', 'B003', '2024-01-20'),
    ('R001', 'B005', '2024-01-20'),
    ('R002', 'B002', '2024-02-25'),
    ('R002', 'B004', '2024-02-25'),
    ('R003', 'B001', '2024-03-15'),
    ('R003', 'B006', '2024-03-15'),
    ('R004', 'B005', '2024-04-10'),
    ('R004', 'B007', '2024-04-10'),
    ('R005', 'B003', '2024-05-20'),
    ('R005', 'B008', '2024-05-20');


INSERT INTO TRANSACTIONS (Transaction_ID, User_ID, Book_ID, Borrow_Date, Due_Date, Return_Date, Status, Fine_Amount)
VALUES 
    ('T001', 'R001', 'B001', '2024-06-01', '2024-06-15', '2024-06-14', 'Returned', 0.00),
    ('T002', 'R001', 'B005', '2024-07-10', '2024-07-24', NULL, 'Active', 0.00),
    ('T003', 'R002', 'B002', '2024-06-15', '2024-06-29', '2024-07-05', 'Returned', 18.00),
    ('T004', 'R003', 'B001', '2024-08-01', '2024-08-15', NULL, 'Active', 0.00),
    ('T005', 'R004', 'B005', '2024-07-20', '2024-08-03', '2024-08-02', 'Returned', 0.00),
    ('T006', 'R005', 'B003', '2024-08-10', '2024-08-24', NULL, 'Active', 0.00),
    ('T007', 'R002', 'B004', '2024-05-15', '2024-05-29', '2024-06-10', 'Returned', 36.00),
    ('T008', 'R001', 'B003', '2024-09-01', '2024-09-15', NULL, 'Active', 0.00);
    
SELECT * FROM TRANSACTIONS;


SELECT * FROM READERS;


SELECT Book_ID, Title, Genre, Total_Copies, Copies_Available 
FROM BOOKS;

-- View all active transactions
SELECT T.Transaction_ID, R.First_Name, R.Last_Name, B.Title, T.Borrow_Date, T.Due_Date, T.Status
FROM TRANSACTIONS T
JOIN READERS R ON T.User_ID = R.User_ID
JOIN BOOKS B ON T.Book_ID = B.Book_ID
WHERE T.Status = 'Active';

--  View books written by each author
SELECT A.First_Name, A.Last_Name, B.Title, W.Author_Role
FROM AUTHORS A
JOIN WRITES W ON A.Author_ID = W.Author_ID
JOIN BOOKS B ON W.Book_ID = B.Book_ID
ORDER BY A.Last_Name;

-- View books managed by each staff member
SELECT S.First_Name, S.Last_Name, S.Position, B.Title
FROM STAFF S
JOIN MANAGES M ON S.Staff_ID = M.Staff_ID
JOIN BOOKS B ON M.Book_ID = B.Book_ID
ORDER BY S.Last_Name;

-- View readers with borrowing privileges
SELECT R.First_Name, R.Last_Name, B.Title, BR.Date_Authorized
FROM READERS R
JOIN BORROWS BR ON R.User_ID = BR.User_ID
JOIN BOOKS B ON BR.Book_ID = B.Book_ID
ORDER BY R.Last_Name;

-- View overdue transactions 
SELECT T.Transaction_ID, R.First_Name, R.Last_Name, B.Title, T.Borrow_Date, T.Due_Date,
       DATEDIFF('2024-09-20', T.Due_Date) AS Days_Overdue
FROM TRANSACTIONS T
JOIN READERS R ON T.User_ID = R.User_ID
JOIN BOOKS B ON T.Book_ID = B.Book_ID
WHERE T.Status = 'Active' AND T.Due_Date < '2024-09-20';

-- View total fines collected
SELECT SUM(Fine_Amount) AS Total_Fines_Collected
FROM TRANSACTIONS
WHERE Status = 'Returned' AND Fine_Amount > 0;

-- View books by publisher
SELECT P.Publisher_Name, B.Title, PB.Publication_Year
FROM PUBLISHERS P
JOIN PUBLISHES PB ON P.Publisher_ID = PB.Publisher_ID
JOIN BOOKS B ON PB.Book_ID = B.Book_ID
ORDER BY P.Publisher_Name;

-- View reader borrowing history
SELECT R.First_Name, R.Last_Name, B.Title, T.Borrow_Date, T.Return_Date, T.Status, T.Fine_Amount
FROM READERS R
JOIN TRANSACTIONS T ON R.User_ID = T.User_ID
JOIN BOOKS B ON T.Book_ID = B.Book_ID
ORDER BY R.Last_Name, T.Borrow_Date DESC;


UPDATE BOOKS 
SET Copies_Available = Copies_Available + 1 
WHERE Book_ID = 'B001';


UPDATE TRANSACTIONS 
SET Status = 'Returned', Return_Date = '2024-09-15' 
WHERE Transaction_ID = 'T002';


UPDATE READERS 
SET Phone_Number = '9999999999', Address = '999 New St, City' 
WHERE User_ID = 'R001';


UPDATE STAFF 
SET Position = 'Senior Librarian' 
WHERE Staff_ID = 'S002';


UPDATE TRANSACTIONS 
SET Fine_Amount = 25.00, Status = 'Overdue' 
WHERE Transaction_ID = 'T006' AND Due_Date < CURRENT_DATE;


DELETE FROM BORROWS 
WHERE User_ID = 'R005' AND Book_ID = 'B008';


DELETE FROM TRANSACTIONS 
WHERE Status = 'Returned' AND Return_Date < DATE_SUB(CURRENT_DATE, INTERVAL 1 YEAR);

-- Calculate Fine

DROP FUNCTION IF EXISTS fn_CalculateFine;

DELIMITER //

CREATE FUNCTION fn_CalculateFine(p_due_date DATE, p_return_date DATE)
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE fine DECIMAL(10,2);

    IF p_return_date IS NULL OR p_return_date <= p_due_date THEN
        SET fine = 0;
    ELSE
        SET fine = DATEDIFF(p_return_date, p_due_date) * 5; -- ₹5 per day fine
    END IF;

    RETURN fine;
END //

DELIMITER ;

SELECT fn_CalculateFine('2024-12-10', '2024-12-15');  

DROP FUNCTION IF EXISTS fn_ActiveBorrowCount;

DELIMITER $$

CREATE FUNCTION fn_ActiveBorrowCount(p_user_id VARCHAR(10))
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE active_count INT;

    SELECT COUNT(*) INTO active_count
    FROM TRANSACTIONS
    WHERE User_ID = p_user_id AND Status = 'Active';

    RETURN active_count;
END $$

DELIMITER ;

SELECT fn_ActiveBorrowCount('R001');

DROP PROCEDURE IF EXISTS sp_RegisterReader;

DELIMITER //

-- Register a new reader

DROP PROCEDURE IF EXISTS sp_RegisterReader;

DELIMITER //

CREATE PROCEDURE sp_RegisterReader(
    IN p_first_name VARCHAR(100),
    IN p_last_name VARCHAR(100),
    IN p_email VARCHAR(255),
    IN p_phone VARCHAR(20),
    IN p_address TEXT,
    OUT p_user_id VARCHAR(10)
)
BEGIN
    DECLARE new_id VARCHAR(10);

    -- Generate next User_ID dynamically
    SELECT CONCAT('R', LPAD(COUNT(*) + 1, 3, '0')) INTO new_id FROM READERS;

    -- Insert new reader
    INSERT INTO READERS (User_ID, First_Name, Last_Name, Email, Address, Phone_Number)
    VALUES (new_id, p_first_name, p_last_name, p_email, p_address, p_phone);

    -- Return generated ID
    SET p_user_id = new_id;
END //

DELIMITER ;


CALL sp_RegisterReader('John', 'Jaden', 'j23j4@gmail.com', '9846993210', 'Bangalore', @newid);
SELECT @newid;

-- Borrow Book
 DROP PROCEDURE IF EXISTS sp_BorrowBook;
 
 DELIMITER //

DROP PROCEDURE IF EXISTS sp_BorrowBook;

DELIMITER //

CREATE PROCEDURE sp_BorrowBook(
    IN p_transaction_id VARCHAR(10),
    IN p_user_id VARCHAR(10),
    IN p_book_id VARCHAR(10),
    IN p_due_date DATE
)
BEGIN
    DECLARE available INT;

    -- Check available copies
    SELECT Copies_Available INTO available
    FROM BOOKS
    WHERE Book_ID = p_book_id;

    -- If copies are available, allow borrowing
    IF available > 0 THEN
        INSERT INTO TRANSACTIONS (Transaction_ID, User_ID, Book_ID, Borrow_Date, Due_Date, Status)
        VALUES (p_transaction_id, p_user_id, p_book_id, CURRENT_TIMESTAMP, p_due_date, 'Active');

        -- Reduce available copies
        UPDATE BOOKS
        SET Copies_Available = Copies_Available - 1
        WHERE Book_ID = p_book_id;
    ELSE
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'No copies available for this book';
    END IF;
END //

DELIMITER ;


CALL sp_BorrowBook('T010', 'R001', 'B001', '2025-11-10');

-- Return Book
DROP PROCEDURE IF EXISTS sp_ReturnBook;
DELIMITER //
CREATE PROCEDURE sp_ReturnBook(
    IN p_transaction_id VARCHAR(10),
    IN p_return_date DATE
)
BEGIN
    DECLARE v_book_id VARCHAR(10);
    DECLARE v_due_date DATE;
    DECLARE fine DECIMAL(10,2);

    SELECT Book_ID, Due_Date INTO v_book_id, v_due_date
    FROM Transactions
    WHERE Transaction_ID = p_transaction_id;

    SET fine = fn_CalculateFine(v_due_date, p_return_date);

    UPDATE Transactions
    SET Return_Date = p_return_date,
        Fine_Amount = fine,
        Status = 'Returned'
    WHERE Transaction_ID = p_transaction_id;

    UPDATE Books
    SET Copies_Available = Copies_Available + 1
    WHERE Book_ID = v_book_id;
END //
DELIMITER ;

CALL sp_ReturnBook('T010', '2025-11-10');

-- Trigger: Auto Update book copies
DROP TRIGGER IF EXISTS trg_after_borrow;
DELIMITER //
CREATE TRIGGER trg_after_borrow
AFTER INSERT ON Transactions
FOR EACH ROW
BEGIN
    UPDATE Books
    SET Copies_Available = Copies_Available - 1
    WHERE Book_ID = NEW.Book_ID;
END //
DELIMITER ;


SELECT Book_ID, Title, Copies_Available FROM Books;

INSERT INTO Transactions (Transaction_ID, User_ID, Book_ID, Due_Date)
VALUES ('T200', 'R001', 'B001', '2025-12-10');

SELECT Copies_Available FROM Books WHERE Book_ID = 'B001';

UPDATE Transactions
SET Status = 'Returned', Return_Date = '2025-12-12'
WHERE Transaction_ID = 'T200';

SELECT Copies_Available FROM Books WHERE Book_ID = 'B001';

DELIMITER $$

DROP TRIGGER IF EXISTS trg_MarkOverdueBooks;

DELIMITER $$

CREATE TRIGGER trg_MarkOverdueBooks
BEFORE UPDATE ON TRANSACTIONS
FOR EACH ROW
BEGIN
    IF (OLD.Return_Date <> NEW.Return_Date OR OLD.Due_Date <> NEW.Due_Date) THEN
        IF NEW.Return_Date IS NULL AND NEW.Due_Date < CURDATE() THEN
            SET NEW.Status = 'Overdue';
        END IF;
    END IF;
END $$

DELIMITER ;


UPDATE TRANSACTIONS
SET Due_Date = '2024-10-01'
WHERE Transaction_ID = 'T004';



SHOW TRIGGERS;

SELECT * FROM TRANSACTIONS;







