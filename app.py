import streamlit as st
from db_conn import run_query, run_command, call_procedure, call_function
import pandas as pd
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(page_title="Library Management System", page_icon="📚", layout="wide")

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
    }
    .section-header {
        color: #2e7d32;
        border-bottom: 2px solid #2e7d32;
        padding-bottom: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">📚 Library Management System</h1>', unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.title("Navigation Menu")
main_menu = st.sidebar.radio(
    "Select Module:",
    ["🏠 Home", "👥 Readers", "📖 Books", "✍️ Authors", "🏢 Publishers", 
     "👔 Staff", "📋 Transactions", "📊 Reports & Analytics"]
)

# ==================== HOME ====================
if main_menu == "🏠 Home":
    st.markdown("## Welcome to the Library Management System")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_books = run_query("SELECT COUNT(*) as count FROM BOOKS")
        st.metric("Total Books", total_books['count'][0] if total_books is not None else 0)
    
    with col2:
        total_readers = run_query("SELECT COUNT(*) as count FROM READERS")
        st.metric("Total Readers", total_readers['count'][0] if total_readers is not None else 0)
    
    with col3:
        active_transactions = run_query("SELECT COUNT(*) as count FROM TRANSACTIONS WHERE Status = 'Active'")
        st.metric("Active Loans", active_transactions['count'][0] if active_transactions is not None else 0)
    
    with col4:
        total_fines = run_query("SELECT SUM(Fine_Amount) as total FROM TRANSACTIONS WHERE Status = 'Returned'")
        fine_val = total_fines['total'][0] if total_fines is not None and total_fines['total'][0] is not None else 0
        st.metric("Total Fines Collected", f"₹{fine_val:.2f}")
    
    st.markdown("---")
    st.markdown("### 🎯 Quick Actions")
    qcol1, qcol2, qcol3 = st.columns(3)
    
    with qcol1:
        st.info("**Register New Reader**\nGo to Readers → Add Reader")
    with qcol2:
        st.info("**Borrow a Book**\nGo to Transactions → Borrow Book")
    with qcol3:
        st.info("**View Reports**\nGo to Reports & Analytics")

# ==================== READERS MODULE ====================
elif main_menu == "👥 Readers":
    st.markdown('<h2 class="section-header">👥 Readers Management</h2>', unsafe_allow_html=True)
    
    reader_tab = st.tabs(["View All Readers", "Add Reader", "Update Reader", "Delete Reader", "Reader Details"])
    
    # View All Readers
    with reader_tab[0]:
        st.subheader("All Registered Readers")
        df = run_query("SELECT * FROM READERS ORDER BY Registration_Date DESC")
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True)
            st.info(f"Total Readers: {len(df)}")
        else:
            st.warning("No readers found.")
    
    # Add Reader (Using Stored Procedure)
    with reader_tab[1]:
        st.subheader("Register New Reader")
        with st.form("add_reader_form"):
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name*")
                email = st.text_input("Email*")
                phone = st.text_input("Phone Number")
            with col2:
                last_name = st.text_input("Last Name*")
                address = st.text_area("Address")
            
            submitted = st.form_submit_button("Register Reader")
            
            if submitted:
                if first_name and last_name and email:
                    try:
                        # Call stored procedure
                        result = call_procedure(
                            "sp_RegisterReader",
                            [first_name, last_name, email, phone, address]
                        )
                        st.success(f"✅ Reader registered successfully! User ID: {result}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    st.error("Please fill all required fields (marked with *)")
    
    # Update Reader
    with reader_tab[2]:
        st.subheader("Update Reader Information")
        readers_df = run_query("SELECT User_ID, CONCAT(First_Name, ' ', Last_Name) as Name FROM READERS")
        if readers_df is not None and not readers_df.empty:
            reader_options = dict(zip(readers_df['Name'], readers_df['User_ID']))
            selected_reader = st.selectbox("Select Reader", options=list(reader_options.keys()))
            
            if selected_reader:
                user_id = reader_options[selected_reader]
                reader_info = run_query(f"SELECT * FROM READERS WHERE User_ID = '{user_id}'")
                
                if reader_info is not None and not reader_info.empty:
                    with st.form("update_reader_form"):
                        col1, col2 = st.columns(2)
                        with col1:
                            new_phone = st.text_input("Phone Number", value=reader_info['Phone_Number'][0] or "")
                        with col2:
                            new_address = st.text_area("Address", value=reader_info['Address'][0] or "")
                        
                        update_submit = st.form_submit_button("Update Reader")
                        
                        if update_submit:
                            command = "UPDATE READERS SET Phone_Number = %s, Address = %s WHERE User_ID = %s"
                            run_command(command, (new_phone, new_address, user_id))
                            st.success("✅ Reader information updated successfully!")
                            st.rerun()
    
    # Delete Reader
    with reader_tab[3]:
        st.subheader("Delete Reader")
        st.warning("⚠️ This action cannot be undone!")
        readers_df = run_query("SELECT User_ID, CONCAT(First_Name, ' ', Last_Name) as Name FROM READERS")
        if readers_df is not None and not readers_df.empty:
            reader_options = dict(zip(readers_df['Name'], readers_df['User_ID']))
            selected_reader = st.selectbox("Select Reader to Delete", options=list(reader_options.keys()))
            
            if st.button("Delete Reader", type="primary"):
                user_id = reader_options[selected_reader]
                run_command("DELETE FROM READERS WHERE User_ID = %s", (user_id,))
                st.success(f"✅ Reader {selected_reader} deleted successfully!")
                st.rerun()
    
    # Reader Details with Active Borrows
    with reader_tab[4]:
        st.subheader("Reader Borrowing History")
        readers_df = run_query("SELECT User_ID, CONCAT(First_Name, ' ', Last_Name) as Name FROM READERS")
        if readers_df is not None and not readers_df.empty:
            reader_options = dict(zip(readers_df['Name'], readers_df['User_ID']))
            selected_reader = st.selectbox("Select Reader", options=list(reader_options.keys()), key="reader_detail")
            
            if selected_reader:
                user_id = reader_options[selected_reader]
                
                # Use function to get active borrow count
                active_count = call_function("fn_ActiveBorrowCount", [user_id])
                st.metric("Currently Borrowed Books", active_count)
                
                # Show borrowing history
                history = run_query(f"""
                    SELECT T.Transaction_ID, B.Title, T.Borrow_Date, T.Due_Date, 
                           T.Return_Date, T.Status, T.Fine_Amount
                    FROM TRANSACTIONS T
                    JOIN BOOKS B ON T.Book_ID = B.Book_ID
                    WHERE T.User_ID = '{user_id}'
                    ORDER BY T.Borrow_Date DESC
                """)
                
                if history is not None and not history.empty:
                    st.dataframe(history, use_container_width=True)
                else:
                    st.info("No borrowing history found.")

# ==================== BOOKS MODULE ====================
elif main_menu == "📖 Books":
    st.markdown('<h2 class="section-header">📖 Books Management</h2>', unsafe_allow_html=True)
    
    book_tab = st.tabs(["View All Books", "Add Book", "Update Book", "Delete Book", "Search Books"])
    
    # View All Books
    with book_tab[0]:
        st.subheader("Library Catalog")
        df = run_query("""
            SELECT B.Book_ID, B.Title, B.ISBN, B.Genre, B.Edition, B.Price,
                   B.Total_Copies, B.Copies_Available,
                   GROUP_CONCAT(CONCAT(A.First_Name, ' ', A.Last_Name) SEPARATOR ', ') as Authors
            FROM BOOKS B
            LEFT JOIN WRITES W ON B.Book_ID = W.Book_ID
            LEFT JOIN AUTHORS A ON W.Author_ID = A.Author_ID
            GROUP BY B.Book_ID
        """)
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True)
            st.info(f"Total Books: {len(df)}")
        else:
            st.warning("No books found.")
    
    # Add Book
    with book_tab[1]:
        st.subheader("Add New Book")
        with st.form("add_book_form"):
            col1, col2 = st.columns(2)
            with col1:
                book_id = st.text_input("Book ID*")
                title = st.text_input("Title*")
                isbn = st.text_input("ISBN*")
                genre = st.text_input("Genre")
            with col2:
                edition = st.text_input("Edition")
                price = st.number_input("Price", min_value=0.0, format="%.2f")
                total_copies = st.number_input("Total Copies", min_value=1, value=1)
                copies_available = st.number_input("Copies Available", min_value=0, value=1)
            
            submitted = st.form_submit_button("Add Book")
            
            if submitted:
                if book_id and title and isbn:
                    command = """
                        INSERT INTO BOOKS (Book_ID, Title, ISBN, Genre, Edition, Price, Total_Copies, Copies_Available)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    run_command(command, (book_id, title, isbn, genre, edition, price, total_copies, copies_available))
                    st.success("✅ Book added successfully!")
                else:
                    st.error("Please fill all required fields (marked with *)")
    
    # Update Book
    with book_tab[2]:
        st.subheader("Update Book Information")
        books_df = run_query("SELECT Book_ID, Title FROM BOOKS")
        if books_df is not None and not books_df.empty:
            book_options = dict(zip(books_df['Title'], books_df['Book_ID']))
            selected_book = st.selectbox("Select Book", options=list(book_options.keys()))
            
            if selected_book:
                book_id = book_options[selected_book]
                book_info = run_query(f"SELECT * FROM BOOKS WHERE Book_ID = '{book_id}'")
                
                if book_info is not None and not book_info.empty:
                    with st.form("update_book_form"):
                        col1, col2 = st.columns(2)
                        with col1:
                            new_price = st.number_input("Price", value=float(book_info['Price'][0]))
                            new_total = st.number_input("Total Copies", value=int(book_info['Total_Copies'][0]))
                        with col2:
                            new_available = st.number_input("Available Copies", value=int(book_info['Copies_Available'][0]))
                        
                        update_submit = st.form_submit_button("Update Book")
                        
                        if update_submit:
                            command = "UPDATE BOOKS SET Price = %s, Total_Copies = %s, Copies_Available = %s WHERE Book_ID = %s"
                            run_command(command, (new_price, new_total, new_available, book_id))
                            st.success("✅ Book information updated successfully!")
                            st.rerun()
    
    # Delete Book
    with book_tab[3]:
        st.subheader("Delete Book")
        st.warning("⚠️ This will also delete associated transactions!")
        books_df = run_query("SELECT Book_ID, Title FROM BOOKS")
        if books_df is not None and not books_df.empty:
            book_options = dict(zip(books_df['Title'], books_df['Book_ID']))
            selected_book = st.selectbox("Select Book to Delete", options=list(book_options.keys()))
            
            if st.button("Delete Book", type="primary"):
                book_id = book_options[selected_book]
                run_command("DELETE FROM BOOKS WHERE Book_ID = %s", (book_id,))
                st.success(f"✅ Book '{selected_book}' deleted successfully!")
                st.rerun()
    
    # Search Books
    with book_tab[4]:
        st.subheader("Search Books")
        search_type = st.radio("Search by:", ["Title", "Genre", "Author"])
        search_term = st.text_input("Enter search term:")
        
        if search_term:
            if search_type == "Title":
                query = f"SELECT * FROM BOOKS WHERE Title LIKE '%{search_term}%'"
            elif search_type == "Genre":
                query = f"SELECT * FROM BOOKS WHERE Genre LIKE '%{search_term}%'"
            else:  # Author
                query = f"""
                    SELECT B.* FROM BOOKS B
                    JOIN WRITES W ON B.Book_ID = W.Book_ID
                    JOIN AUTHORS A ON W.Author_ID = A.Author_ID
                    WHERE CONCAT(A.First_Name, ' ', A.Last_Name) LIKE '%{search_term}%'
                """
            
            results = run_query(query)
            if results is not None and not results.empty:
                st.dataframe(results, use_container_width=True)
            else:
                st.info("No books found matching your search.")

# ==================== AUTHORS MODULE ====================
elif main_menu == "✍️ Authors":
    st.markdown('<h2 class="section-header">✍️ Authors Management</h2>', unsafe_allow_html=True)
    
    author_tab = st.tabs(["View All Authors", "Add Author", "Author Books"])
    
    # View All Authors
    with author_tab[0]:
        st.subheader("All Authors")
        df = run_query("SELECT * FROM AUTHORS")
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No authors found.")
    
    # Add Author
    with author_tab[1]:
        st.subheader("Add New Author")
        with st.form("add_author_form"):
            author_id = st.text_input("Author ID*")
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name*")
            with col2:
                last_name = st.text_input("Last Name*")
            biography = st.text_area("Biography")
            
            submitted = st.form_submit_button("Add Author")
            
            if submitted:
                if author_id and first_name and last_name:
                    command = "INSERT INTO AUTHORS VALUES (%s, %s, %s, %s)"
                    run_command(command, (author_id, first_name, last_name, biography))
                    st.success("✅ Author added successfully!")
                else:
                    st.error("Please fill all required fields")
    
    # Author Books
    with author_tab[2]:
        st.subheader("Books by Author")
        query = """
            SELECT A.First_Name, A.Last_Name, B.Title, W.Author_Role, P.Publication_Year
            FROM AUTHORS A
            JOIN WRITES W ON A.Author_ID = W.Author_ID
            JOIN BOOKS B ON W.Book_ID = B.Book_ID
            LEFT JOIN PUBLISHES P ON B.Book_ID = P.Book_ID
            ORDER BY A.Last_Name, A.First_Name
        """
        df = run_query(query)
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No author-book relationships found.")

# ==================== PUBLISHERS MODULE ====================
elif main_menu == "🏢 Publishers":
    st.markdown('<h2 class="section-header">🏢 Publishers Management</h2>', unsafe_allow_html=True)
    
    pub_tab = st.tabs(["View All Publishers", "Add Publisher", "Publisher Books"])
    
    # View All Publishers
    with pub_tab[0]:
        st.subheader("All Publishers")
        df = run_query("SELECT * FROM PUBLISHERS")
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No publishers found.")
    
    # Add Publisher
    with pub_tab[1]:
        st.subheader("Add New Publisher")
        with st.form("add_publisher_form"):
            pub_id = st.text_input("Publisher ID*")
            pub_name = st.text_input("Publisher Name*")
            address = st.text_area("Address")
            contact_email = st.text_input("Contact Email")
            
            submitted = st.form_submit_button("Add Publisher")
            
            if submitted:
                if pub_id and pub_name:
                    command = "INSERT INTO PUBLISHERS VALUES (%s, %s, %s, %s)"
                    run_command(command, (pub_id, pub_name, address, contact_email))
                    st.success("✅ Publisher added successfully!")
                else:
                    st.error("Please fill all required fields")
    
    # Publisher Books
    with pub_tab[2]:
        st.subheader("Books by Publisher")
        query = """
            SELECT P.Publisher_Name, B.Title, PB.Publication_Year, B.Genre
            FROM PUBLISHERS P
            JOIN PUBLISHES PB ON P.Publisher_ID = PB.Publisher_ID
            JOIN BOOKS B ON PB.Book_ID = B.Book_ID
            ORDER BY P.Publisher_Name, PB.Publication_Year DESC
        """
        df = run_query(query)
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No publisher-book relationships found.")

# ==================== STAFF MODULE ====================
elif main_menu == "👔 Staff":
    st.markdown('<h2 class="section-header">👔 Staff Management</h2>', unsafe_allow_html=True)
    
    staff_tab = st.tabs(["View All Staff", "Add Staff", "Staff Assignments"])
    
    # View All Staff
    with staff_tab[0]:
        st.subheader("Library Staff")
        df = run_query("SELECT * FROM STAFF")
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No staff members found.")
    
    # Add Staff
    with staff_tab[1]:
        st.subheader("Add New Staff Member")
        with st.form("add_staff_form"):
            staff_id = st.text_input("Staff ID*")
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name*")
                email = st.text_input("Email*")
            with col2:
                last_name = st.text_input("Last Name*")
                position = st.text_input("Position*")
            
            submitted = st.form_submit_button("Add Staff")
            
            if submitted:
                if staff_id and first_name and last_name and email and position:
                    command = "INSERT INTO STAFF VALUES (%s, %s, %s, %s, %s)"
                    run_command(command, (staff_id, first_name, last_name, email, position))
                    st.success("✅ Staff member added successfully!")
                else:
                    st.error("Please fill all required fields")
    
    # Staff Assignments
    with staff_tab[2]:
        st.subheader("Books Managed by Staff")
        query = """
            SELECT S.First_Name, S.Last_Name, S.Position, B.Title, B.Book_ID
            FROM STAFF S
            JOIN MANAGES M ON S.Staff_ID = M.Staff_ID
            JOIN BOOKS B ON M.Book_ID = B.Book_ID
            ORDER BY S.Last_Name
        """
        df = run_query(query)
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No staff-book assignments found.")

# ==================== TRANSACTIONS MODULE ====================
elif main_menu == "📋 Transactions":
    st.markdown('<h2 class="section-header">📋 Transaction Management</h2>', unsafe_allow_html=True)
    
    trans_tab = st.tabs(["Active Transactions", "Borrow Book", "Return Book", "Transaction History"])
    
    # Active Transactions
    with trans_tab[0]:
        st.subheader("Currently Active Loans")
        query = """
            SELECT T.Transaction_ID, 
                   CONCAT(R.First_Name, ' ', R.Last_Name) as Reader,
                   B.Title as Book,
                   T.Borrow_Date, T.Due_Date,
                   DATEDIFF(CURDATE(), T.Due_Date) as Days_Overdue,
                   T.Status
            FROM TRANSACTIONS T
            JOIN READERS R ON T.User_ID = R.User_ID
            JOIN BOOKS B ON T.Book_ID = B.Book_ID
            WHERE T.Status = 'Active'
            ORDER BY T.Due_Date
        """
        df = run_query(query)
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No active transactions.")
    
    # Borrow Book (Using Stored Procedure)
    with trans_tab[1]:
        st.subheader("Issue a Book")
        
        with st.form("borrow_book_form"):
            # Get available books
            available_books = run_query("SELECT Book_ID, Title, Copies_Available FROM BOOKS WHERE Copies_Available > 0")
            readers = run_query("SELECT User_ID, CONCAT(First_Name, ' ', Last_Name) as Name FROM READERS")
            
            if available_books is not None and readers is not None:
                col1, col2 = st.columns(2)
                
                with col1:
                    reader_options = dict(zip(readers['Name'], readers['User_ID']))
                    selected_reader = st.selectbox("Select Reader", options=list(reader_options.keys()))
                    
                with col2:
                    book_options = dict(zip(
                        [f"{row['Title']} (Available: {row['Copies_Available']})" 
                         for _, row in available_books.iterrows()],
                        available_books['Book_ID']
                    ))
                    selected_book = st.selectbox("Select Book", options=list(book_options.keys()))
                
                transaction_id = st.text_input("Transaction ID*")
                due_date = st.date_input("Due Date", value=datetime.now() + timedelta(days=14))
                
                submitted = st.form_submit_button("Issue Book")
                
                if submitted and transaction_id:
                    try:
                        user_id = reader_options[selected_reader]
                        book_id = book_options[selected_book]
                        
                        # Call stored procedure
                        call_procedure("sp_BorrowBook", [transaction_id, user_id, book_id, due_date])
                        st.success("✅ Book issued successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("No available books or readers found.")
    
    # Return Book (Using Stored Procedure)
    with trans_tab[2]:
        st.subheader("Return a Book")
        
        active_trans = run_query("""
            SELECT T.Transaction_ID, 
                   CONCAT(R.First_Name, ' ', R.Last_Name) as Reader,
                   B.Title as Book,
                   T.Due_Date
            FROM TRANSACTIONS T
            JOIN READERS R ON T.User_ID = R.User_ID
            JOIN BOOKS B ON T.Book_ID = B.Book_ID
            WHERE T.Status = 'Active'
        """)
        
        if active_trans is not None and not active_trans.empty:
            trans_options = dict(zip(
                [f"{row['Reader']} - {row['Book']} (Due: {row['Due_Date']})" 
                 for _, row in active_trans.iterrows()],
                active_trans['Transaction_ID']
            ))
            
            selected_trans = st.selectbox("Select Transaction", options=list(trans_options.keys()))
            return_date = st.date_input("Return Date", value=datetime.now())
            
            if st.button("Process Return"):
                try:
                    trans_id = trans_options[selected_trans]
                    
                    # Get due date for fine calculation
                    trans_info = run_query(f"SELECT Due_Date FROM TRANSACTIONS WHERE Transaction_ID = '{trans_id}'")
                    due_date = trans_info['Due_Date'][0]
                    
                    # Calculate fine using function
                    fine = call_function("fn_CalculateFine", [due_date, return_date])
                    
                    # Call return procedure
                    call_procedure("sp_ReturnBook", [trans_id, return_date])
                    
                    if fine > 0:
                        st.warning(f"⚠️ Book returned with a fine of ₹{fine:.2f}")
                    else:
                        st.success("✅ Book returned successfully! No fine.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.info("No active transactions to return.")
    
    # Transaction History
    with trans_tab[3]:
        st.subheader("Complete Transaction History")
        query = """
            SELECT T.Transaction_ID,
                   CONCAT(R.First_Name, ' ', R.Last_Name) as Reader,
                   B.Title as Book,
                   T.Borrow_Date, T.Due_Date, T.Return_Date,
                   T.Status, T.Fine_Amount
            FROM TRANSACTIONS T
            JOIN READERS R ON T.User_ID = R.User_ID
            JOIN BOOKS B ON T.Book_ID = B.Book_ID
            ORDER BY T.Borrow_Date DESC
        """
        df = run_query(query)
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No transaction history.")

# ==================== REPORTS & ANALYTICS ====================
elif main_menu == "📊 Reports & Analytics":
    st.markdown('<h2 class="section-header">📊 Reports & Analytics</h2>', unsafe_allow_html=True)
    
    report_tab = st.tabs([
        "Overdue Books", "Popular Books", "Reader Statistics", 
        "Fine Collection", "Genre Distribution", "Custom Query"
    ])
    
    # Overdue Books
    with report_tab[0]:
        st.subheader("Overdue Books Report")
        query = """
            SELECT T.Transaction_ID,
                   CONCAT(R.First_Name, ' ', R.Last_Name) as Reader,
                   R.Phone_Number,
                   B.Title as Book,
                   T.Borrow_Date, T.Due_Date,
                   DATEDIFF(CURDATE(), T.Due_Date) as Days_Overdue
            FROM TRANSACTIONS T
            JOIN READERS R ON T.User_ID = R.User_ID
            JOIN BOOKS B ON T.Book_ID = B.Book_ID
            WHERE T.Status = 'Active' AND T.Due_Date < CURDATE()
            ORDER BY Days_Overdue DESC
        """
        df = run_query(query)
        if df is not None and not df.empty:
            st.error(f"⚠️ {len(df)} overdue transactions found!")
            st.dataframe(df, use_container_width=True)
        else:
            st.success("✅ No overdue books!")
    
    # Popular Books
    with report_tab[1]:
        st.subheader("Most Borrowed Books")
        query = """
            SELECT B.Title, B.Genre,
                   COUNT(T.Transaction_ID) as Borrow_Count,
                   B.Copies_Available,
                   CONCAT(A.First_Name, ' ', A.Last_Name) as Author
            FROM BOOKS B
            LEFT JOIN TRANSACTIONS T ON B.Book_ID = T.Book_ID
            LEFT JOIN WRITES W ON B.Book_ID = W.Book_ID
            LEFT JOIN AUTHORS A ON W.Author_ID = A.Author_ID
            GROUP BY B.Book_ID
            ORDER BY Borrow_Count DESC
            LIMIT 10
        """
        df = run_query(query)
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True)
            
            # Visualization
            import plotly.express as px
            fig = px.bar(df, x='Title', y='Borrow_Count', title='Top 10 Most Borrowed Books')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No borrowing data available.")
    
    # Reader Statistics
    with report_tab[2]:
        st.subheader("Reader Borrowing Statistics")
        query = """
            SELECT CONCAT(R.First_Name, ' ', R.Last_Name) as Reader,
                   R.Email,
                   COUNT(T.Transaction_ID) as Total_Borrows,
                   SUM(CASE WHEN T.Status = 'Active' THEN 1 ELSE 0 END) as Active_Borrows,
                   SUM(T.Fine_Amount) as Total_Fines_Paid
            FROM READERS R
            LEFT JOIN TRANSACTIONS T ON R.User_ID = T.User_ID
            GROUP BY R.User_ID
            ORDER BY Total_Borrows DESC
        """
        df = run_query(query)
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No reader statistics available.")
    
    # Fine Collection
    with report_tab[3]:
        st.subheader("Fine Collection Report")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_fines = run_query("SELECT SUM(Fine_Amount) as total FROM TRANSACTIONS WHERE Status = 'Returned' AND Fine_Amount > 0")
            fine_val = total_fines['total'][0] if total_fines is not None and total_fines['total'][0] is not None else 0
            st.metric("Total Fines Collected", f"₹{fine_val:.2f}")
        
        with col2:
            pending_fines = run_query("""
                SELECT SUM(fn_CalculateFine(Due_Date, CURDATE())) as total 
                FROM TRANSACTIONS 
                WHERE Status = 'Active' AND Due_Date < CURDATE()
            """)
            pending_val = pending_fines['total'][0] if pending_fines is not None and pending_fines['total'][0] is not None else 0
            st.metric("Pending Fines", f"₹{pending_val:.2f}")
        
        with col3:
            fine_transactions = run_query("SELECT COUNT(*) as count FROM TRANSACTIONS WHERE Fine_Amount > 0")
            st.metric("Transactions with Fines", fine_transactions['count'][0] if fine_transactions is not None else 0)
        
        st.markdown("---")
        
        # Detailed fine report
        query = """
            SELECT T.Transaction_ID,
                   CONCAT(R.First_Name, ' ', R.Last_Name) as Reader,
                   B.Title as Book,
                   T.Borrow_Date, T.Due_Date, T.Return_Date,
                   T.Fine_Amount,
                   T.Status
            FROM TRANSACTIONS T
            JOIN READERS R ON T.User_ID = R.User_ID
            JOIN BOOKS B ON T.Book_ID = B.Book_ID
            WHERE T.Fine_Amount > 0
            ORDER BY T.Fine_Amount DESC
        """
        df = run_query(query)
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No fines recorded.")
    
    # Genre Distribution
    with report_tab[4]:
        st.subheader("Books by Genre")
        query = """
            SELECT Genre, 
                   COUNT(*) as Book_Count,
                   SUM(Total_Copies) as Total_Copies,
                   SUM(Copies_Available) as Available_Copies
            FROM BOOKS
            WHERE Genre IS NOT NULL
            GROUP BY Genre
            ORDER BY Book_Count DESC
        """
        df = run_query(query)
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True)
            
            # Pie chart
            try:
                import plotly.express as px
                fig = px.pie(df, values='Book_Count', names='Genre', title='Book Distribution by Genre')
                st.plotly_chart(fig, use_container_width=True)
            except:
                st.info("Install plotly for visualizations: pip install plotly")
        else:
            st.info("No genre data available.")
    
    # Custom Query
    with report_tab[5]:
        st.subheader("Run Custom SQL Query")
        st.warning("⚠️ Use with caution! Only SELECT queries recommended.")
        
        custom_query = st.text_area("Enter SQL Query:", height=150, 
                                     value="SELECT * FROM BOOKS LIMIT 10")
        
        if st.button("Execute Query"):
            try:
                result = run_query(custom_query)
                if result is not None and not result.empty:
                    st.success(f"✅ Query executed successfully! Rows returned: {len(result)}")
                    st.dataframe(result, use_container_width=True)
                else:
                    st.info("Query executed but returned no results.")
            except Exception as e:
                st.error(f"❌ Query Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>Library Management System | Built with Streamlit & MySQL</p>
    </div>
""", unsafe_allow_html=True)