# Library Management System

A comprehensive web-based Library Management System built with **Python (Streamlit)** and **MySQL**. This project demonstrates advanced database concepts including stored procedures, triggers, functions, and complex SQL queries integrated with a modern, user-friendly interface.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## Project Overview

This Library Management System automates and streamlines library operations, replacing manual record-keeping with an efficient digital solution. The system provides a centralized platform for managing library resources, tracking book circulation, maintaining reader records, and generating analytical reports.

---

## Key Features

### Core Functionality
- **Reader Management**: Register, update, delete readers with auto-generated IDs
- **Book Catalog**: Complete CRUD operations for books, authors, and publishers
- **Transaction Processing**: Issue and return books with automated fine calculation
- **Staff Management**: Manage library staff and book assignments
- **Advanced Search**: Search books by title, genre, or author

### Database Features
- **Stored Procedures** (3):
  - `sp_RegisterReader` - Auto-generates User IDs
  - `sp_BorrowBook` - Validates availability and issues books
  - `sp_ReturnBook` - Processes returns with fine calculation

- **Stored Functions** (2):
  - `fn_CalculateFine` - Calculates late fees (₹5/day)
  - `fn_ActiveBorrowCount` - Counts active borrows per reader

- **Triggers** (2):
  - `trg_after_borrow` - Auto-decrements available copies
  - `trg_MarkOverdueBooks` - Auto-marks overdue transactions

### Reports & Analytics
- Overdue books report with contact information
- Most borrowed books (Top 10) with visualizations
- Reader statistics and borrowing patterns
- Fine collection summary
- Genre distribution with pie charts
- Custom SQL query executor

---

## System Architecture

### Database Schema
The system uses 11 normalized tables following 3NF:

**Core Tables:**
- `READERS` - Reader information and registration
- `BOOKS` - Book catalog with inventory tracking
- `AUTHORS` - Author details and biographies
- `PUBLISHERS` - Publisher information
- `STAFF` - Library staff members
- `TRANSACTIONS` - Borrowing records and fines

**Relationship Tables:**
- `WRITES` - Author-Book relationship (Many-to-Many)
- `PUBLISHES` - Publisher-Book relationship
- `MANAGES` - Staff-Book management assignments
- `BORROWS` - Reader-Book borrowing authorization
- `AUTH_CREDENTIALS` - Staff authentication (1:1 with Staff)

### Technology Stack

**Backend:**
- Python 3.8+
- MySQL 8.0+
- mysql-connector-python

**Frontend:**
- Streamlit 1.28+
- Pandas (Data manipulation)
- Plotly (Data visualization)

**Development Tools:**
- Visual Studio Code
- MySQL Workbench
- Git & GitHub

---

## 🚀 Installation & Setup

### Prerequisites
```bash
# Check Python version (3.8+ required)
python --version

# Check MySQL version (8.0+ required)
mysql --version
```

### Step 1: Clone the Repository
```bash
git clone https://github.com/BhumikaGupta25/lib_management.git
cd lib_management
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Setup MySQL Database
```bash
# Login to MySQL
mysql -u root -p

# Run the SQL script
source library_database.sql

# Or import via MySQL Workbench:
# File → Run SQL Script → Select library_database.sql
```

### Step 4: Configure Database Connection
Edit `db_conn.py` with your MySQL credentials:
```python
DB_HOST = '127.0.0.1'
DB_USER = 'root'          # Your MySQL username
DB_PASS = 'your_password' # Your MySQL password
DB_NAME = 'Library'
```

### Step 5: Test Database Connection
```bash
python db_conn.py
```

Expected output:
```
✅ Connection test successful!
Successfully connected to MySQL Server version 8.0.x
Connected to database: Library
```

### Step 6: Run the Application
```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

---

## Usage Guide

### For Librarians

#### 1. Register a New Reader
```
Navigation: Readers → Add Reader
- Fill in reader details
- System auto-generates User ID (e.g., R001, R002...)
- Click "Register Reader"
```

#### 2️. Add Books to Catalog
```
Navigation: Books → Add Book
- Enter book details (Title, ISBN, Genre, etc.)
- Specify total copies and available copies
- Click "Add Book"
```

#### 3️. Issue a Book
```
Navigation: Transactions → Borrow Book
- Select reader from dropdown
- Select available book
- Enter unique Transaction ID
- Set due date (default: 14 days)
- Click "Issue Book"

Result: Available copies automatically decrease (via trigger)
```

#### 4️. Return a Book
```
Navigation: Transactions → Return Book
- Select active transaction
- Set return date
- Click "Process Return"

Result: Fine automatically calculated if overdue (₹5/day)
        Available copies automatically increase
```

#### 5️. View Reports
```
Navigation: Reports & Analytics
- Overdue Books: See late returns with contact info
- Popular Books: Top 10 most borrowed
- Reader Statistics: Borrowing patterns
- Fine Collection: Total fines collected
- Genre Distribution: Visual breakdown
```

---

## Feature Demonstrations

### Trigger Demonstration

**Trigger 1: Auto-Decrement Copies**
```
1. Go to Books → View All Books
2. Note: "Harry Potter" has 6 copies available
3. Go to Transactions → Borrow Book
4. Borrow "Harry Potter"
5. Return to Books page
6. Result: Now shows 5 copies ✅ (trg_after_borrow)
```

**Trigger 2: Auto-Mark Overdue**
```
1. Go to Reports & Analytics → Trigger Demo
2. Select an active transaction
3. Set due date to past (e.g., 5 days ago)
4. Click "Test Trigger"
5. Check Transaction History
6. Result: Status changed to "Overdue" ✅ (trg_MarkOverdueBooks)
```

---

## Database Queries

### Complex JOIN Query
```sql
-- Books with Authors and Publishers
SELECT B.Title, 
       CONCAT(A.First_Name, ' ', A.Last_Name) as Author,
       P.Publisher_Name,
       PB.Publication_Year,
       B.Genre
FROM BOOKS B
JOIN WRITES W ON B.Book_ID = W.Book_ID
JOIN AUTHORS A ON W.Author_ID = A.Author_ID
JOIN PUBLISHES PB ON B.Book_ID = PB.Book_ID
JOIN PUBLISHERS P ON PB.Publisher_ID = P.Publisher_ID
ORDER BY B.Title;
```

### Nested Subquery
```sql
-- Readers who borrowed more than average
SELECT R.First_Name, R.Last_Name,
       (SELECT COUNT(*) FROM TRANSACTIONS T 
        WHERE T.User_ID = R.User_ID) as Total_Borrows
FROM READERS R
WHERE (SELECT COUNT(*) FROM TRANSACTIONS T 
       WHERE T.User_ID = R.User_ID) > 
      (SELECT AVG(borrow_count) FROM 
          (SELECT COUNT(*) as borrow_count 
           FROM TRANSACTIONS GROUP BY User_ID) as avg_borrows)
ORDER BY Total_Borrows DESC;
```

### Aggregate Query
```sql
-- Genre-wise Statistics
SELECT B.Genre,
       COUNT(DISTINCT B.Book_ID) as Total_Books,
       AVG(B.Price) as Average_Price,
       SUM(B.Total_Copies) as Total_Inventory,
       COUNT(T.Transaction_ID) as Total_Borrows
FROM BOOKS B
LEFT JOIN TRANSACTIONS T ON B.Book_ID = T.Book_ID
WHERE B.Genre IS NOT NULL
GROUP BY B.Genre
HAVING COUNT(DISTINCT B.Book_ID) > 0
ORDER BY Total_Borrows DESC;
```

---

## Project Structure

```
library-management-system/
│
├── app.py                      # Main Streamlit application
├── db_conn.py                  # Database connection utilities
├── library_database.sql        # Complete SQL script
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
│
├── screenshots/                # Application screenshots
│   ├── home_dashboard.png
│   ├── reader_management.png
│   ├── book_catalog.png
│   ├── transactions.png
│   └── reports.png
│
├── documentation/              # Additional documents
│   ├── ER_Diagram.pdf
│   ├── Relational_Schema.pdf
│   └── User_Requirements.pdf
│
└── .gitignore                  # Git ignore file
```

---

## Security Features

-  Parameterized queries to prevent SQL injection
-  Input validation on all forms
-  Transaction rollback on errors
-  Database constraints (CHECK, FOREIGN KEY)
-  Email format validation
-  Data type enforcement

---

##  Testing

### Run Test Data
```bash
# Login to MySQL
mysql -u root -p Library

# Run test script
source sample_test_data.sql
```

### Verify Installation
```bash
# Test database connection
python db_conn.py

# Check all procedures exist
mysql -u root -p -e "SHOW PROCEDURE STATUS WHERE Db = 'Library';"

# Check all functions exist
mysql -u root -p -e "SHOW FUNCTION STATUS WHERE Db = 'Library';"

# Check all triggers exist
mysql -u root -p -e "SHOW TRIGGERS FROM Library;"
```

---

##  Future Enhancements

- [ ] User authentication with role-based access control
- [ ] Email/SMS notifications for due dates
- [ ] Barcode/QR code scanning
- [ ] Mobile responsive design
- [ ] Book reservation system
- [ ] Multi-library branch support
- [ ] Integration with online book databases
- [ ] Advanced analytics dashboard
- [ ] Export reports to PDF/Excel
- [ ] Book recommendation engine

---

##  Known Issues

- Password storage in plain text (should implement hashing)
- No user session management
- Single database connection (no connection pooling)
- Limited to single library location

---

##  Contributing

This is an academic project, but suggestions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📸 Screenshots

### Home Dashboard
<img width="1835" height="856" alt="image" src="https://github.com/user-attachments/assets/e1deb994-4248-473d-b695-4743c7377ea2" />

###Readers list
<img width="1835" height="810" alt="image" src="https://github.com/user-attachments/assets/50332dbe-a51f-4806-abe0-4091ee187634" />
<img width="1790" height="747" alt="image" src="https://github.com/user-attachments/assets/a52f7b9b-02d0-4a61-8ad0-f764e2e931ae" />
<img width="1756" height="775" alt="image" src="https://github.com/user-attachments/assets/20beabca-d874-42ff-97b8-5c84f6b01482" />
<img width="1791" height="737" alt="image" src="https://github.com/user-attachments/assets/c520dfcc-6c7c-470e-860c-c5ba55b0d5f2" />
<img width="1795" height="802" alt="image" src="https://github.com/user-attachments/assets/c0e44d83-17cf-474b-83ee-b274bc683859" />

### Book Catalog
<img width="1829" height="872" alt="image" src="https://github.com/user-attachments/assets/687b1a2e-0f5f-416b-baff-ccdfb73e3e22" />
<img width="1762" height="805" alt="image" src="https://github.com/user-attachments/assets/a341eaba-6290-444c-b8ef-73f94e543064" />
<img width="1791" height="762" alt="image" src="https://github.com/user-attachments/assets/6efe6cc2-6e54-4e1c-abd9-a52aa38d7c45" />
<img width="1772" height="670" alt="image" src="https://github.com/user-attachments/assets/4c97ada3-80f8-43b6-9bd4-1323521d4a6f" />
<img width="1828" height="668" alt="image" src="https://github.com/user-attachments/assets/f9d750e6-64e9-4766-b006-39c8a504a606" />

### List of Authors 
<img width="1835" height="829" alt="image" src="https://github.com/user-attachments/assets/85d949f9-2049-4d97-8629-8d6e8ec872ff" />
<img width="1824" height="815" alt="image" src="https://github.com/user-attachments/assets/1f6134b8-ec88-49c5-aef3-16a30e24e967" />
<img width="1791" height="772" alt="image" src="https://github.com/user-attachments/assets/5556808e-3f31-4d79-9475-3f5d64c2a0ef" />

### List of Publishers 
<img width="1841" height="818" alt="image" src="https://github.com/user-attachments/assets/0322768c-74fc-4180-ae90-90be5773549b" />
<img width="1805" height="840" alt="image" src="https://github.com/user-attachments/assets/9237f52f-62a9-4804-91b9-f6fbe6f78da8" />
<img width="1790" height="784" alt="image" src="https://github.com/user-attachments/assets/8a12eb34-b79d-4afa-a806-e186d412f615" />

### List of Staff
<img width="1832" height="849" alt="image" src="https://github.com/user-attachments/assets/f9b2f5fe-680b-4d18-8493-ab3613a9cbca" />
<img width="1805" height="759" alt="image" src="https://github.com/user-attachments/assets/1ab45b12-17c5-4487-8d86-aa42338ce23b" />
<img width="1754" height="777" alt="image" src="https://github.com/user-attachments/assets/c2930b3b-de7b-4972-87ae-c2028eb64152" />

### Transaction Management
<img width="1799" height="719" alt="image" src="https://github.com/user-attachments/assets/fda2887f-4730-4061-aec7-dfb62b9416a3" />
<img width="1796" height="819" alt="image" src="https://github.com/user-attachments/assets/2ac42a22-71ac-4df1-853c-776b791c1a59" />
<img width="1838" height="723" alt="image" src="https://github.com/user-attachments/assets/adae1ce7-7f7b-40b6-a23b-9f2e079b9f1a" />
<img width="1831" height="829" alt="image" src="https://github.com/user-attachments/assets/8ab5e92f-4293-4363-9028-386170930da1" />

### Reports & Analytics
<img width="1800" height="656" alt="image" src="https://github.com/user-attachments/assets/2f70ca43-35ae-4122-8c17-a7fc739ce621" />
<img width="1795" height="787" alt="image" src="https://github.com/user-attachments/assets/e2ce3f64-2e39-416f-b986-31140d06254e" />
<img width="1803" height="801" alt="image" src="https://github.com/user-attachments/assets/6f05a42d-1faa-4445-9dde-8ebd9191cbd5" />
<img width="1809" height="873" alt="image" src="https://github.com/user-attachments/assets/df4ef9ce-4bf0-403d-9057-18159c6d42d6" />
<img width="1805" height="785" alt="image" src="https://github.com/user-attachments/assets/ada7ca40-eca5-4834-948c-75c7599fa8ab" />


---

## 🌟 Star this Repository!

If you find this project helpful, please give it a ⭐ on GitHub!

---

<div align="center">

**Built using Python, MySQL, and Streamlit**
system/issues)

</div>
