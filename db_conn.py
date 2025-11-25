import mysql.connector
from mysql.connector import Error
import pandas as pd

# Database Configuration
DB_HOST = '127.0.0.1'
DB_USER = 'root'
DB_PASS = 'Bhumika@123'  # Change this to your password
DB_NAME = 'Library'

def create_connection():
    """Create and return a database connection"""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            autocommit=False  # Enable transaction control
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

def run_query(query, params=None):
    """Execute a SELECT query and return results as DataFrame"""
    conn = create_connection()
    df = None
    if conn:
        try:
            if params:
                df = pd.read_sql(query, conn, params=params)
            else:
                df = pd.read_sql(query, conn)
            return df
        except Exception as e:
            print(f"Query Error: {e}")
            return None
        finally:
            if conn.is_connected():
                conn.close()
    return None

def run_command(command, values=None):
    """Execute INSERT, UPDATE, DELETE commands"""
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            if values:
                cursor.execute(command, values)
            else:
                cursor.execute(command)
            conn.commit()
            print(f"Command executed successfully. Rows affected: {cursor.rowcount}")
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error during command execution: {e}")
            raise e
        finally:
            cursor.close()
            if conn.is_connected():
                conn.close()
    return False

def call_procedure(proc_name, params=None):
    """
    Call a stored procedure
    
    Args:
        proc_name: Name of the stored procedure
        params: List of parameters to pass to the procedure
    
    Returns:
        Result from the procedure (for OUT parameters)
    """
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # For procedures with OUT parameters (like sp_RegisterReader)
            if proc_name == "sp_RegisterReader":
                # Prepare the call with OUT parameter
                cursor.callproc(proc_name, params + [0])  # Add placeholder for OUT param
                
                # Retrieve OUT parameter
                cursor.execute("SELECT @_sp_RegisterReader_5")
                result = cursor.fetchone()
                conn.commit()
                
                if result:
                    return result[0]  # Return the generated User_ID
                return None
            
            # For sp_ReturnBook - handle manually if procedure doesn't exist
            elif proc_name == "sp_ReturnBook":
                trans_id, return_date = params
                
                # Get transaction details
                cursor.execute(
                    "SELECT Book_ID, Due_Date FROM TRANSACTIONS WHERE Transaction_ID = %s",
                    (trans_id,)
                )
                result = cursor.fetchone()
                
                if not result:
                    raise Exception(f"Transaction {trans_id} not found")
                
                book_id, due_date = result
                
                # Calculate fine
                cursor.execute("SELECT fn_CalculateFine(%s, %s)", (due_date, return_date))
                fine_result = cursor.fetchone()
                fine = fine_result[0] if fine_result else 0
                
                # Update transaction
                cursor.execute(
                    """UPDATE TRANSACTIONS 
                       SET Return_Date = %s, Fine_Amount = %s, Status = 'Returned'
                       WHERE Transaction_ID = %s""",
                    (return_date, fine, trans_id)
                )
                
                # Update book availability
                cursor.execute(
                    "UPDATE BOOKS SET Copies_Available = Copies_Available + 1 WHERE Book_ID = %s",
                    (book_id,)
                )
                
                conn.commit()
                print(f"Book returned successfully. Fine: ₹{fine}")
                return fine
            
            # For procedures without OUT parameters (like sp_BorrowBook)
            else:
                if params:
                    cursor.callproc(proc_name, params)
                else:
                    cursor.callproc(proc_name)
                conn.commit()
                print(f"Procedure {proc_name} executed successfully")
                return True
                
        except Exception as e:
            conn.rollback()
            print(f"Error calling procedure {proc_name}: {e}")
            raise e
        finally:
            cursor.close()
            if conn.is_connected():
                conn.close()
    return None

def call_function(func_name, params=None):
    """
    Call a stored function
    
    Args:
        func_name: Name of the function
        params: List of parameters to pass
    
    Returns:
        Return value from the function
    """
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # Build the SQL call
            if params:
                placeholders = ', '.join(['%s'] * len(params))
                query = f"SELECT {func_name}({placeholders})"
                cursor.execute(query, params)
            else:
                query = f"SELECT {func_name}()"
                cursor.execute(query)
            
            result = cursor.fetchone()
            
            if result:
                return result[0]
            return None
            
        except Exception as e:
            print(f"Error calling function {func_name}: {e}")
            raise e
        finally:
            cursor.close()
            if conn.is_connected():
                conn.close()
    return None

def execute_transaction(commands_list):
    """
    Execute multiple commands as a single transaction
    
    Args:
        commands_list: List of tuples [(command1, values1), (command2, values2), ...]
    
    Returns:
        True if all commands succeed, False otherwise
    """
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            for command, values in commands_list:
                if values:
                    cursor.execute(command, values)
                else:
                    cursor.execute(command)
            
            conn.commit()
            print(f"Transaction completed successfully. {len(commands_list)} commands executed.")
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"Transaction failed: {e}")
            return False
        finally:
            cursor.close()
            if conn.is_connected():
                conn.close()
    return False

def get_table_schema(table_name):
    """Get the schema of a table"""
    query = f"DESCRIBE {table_name}"
    return run_query(query)

def backup_table(table_name):
    """Create a backup of a table"""
    backup_name = f"{table_name}_backup_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"
    command = f"CREATE TABLE {backup_name} AS SELECT * FROM {table_name}"
    return run_command(command)

# Test connection
def test_connection():
    """Test database connection"""
    conn = create_connection()
    if conn:
        if conn.is_connected():
            db_info = conn.get_server_info()
            print(f"Successfully connected to MySQL Server version {db_info}")
            cursor = conn.cursor()
            cursor.execute("SELECT DATABASE();")
            record = cursor.fetchone()
            print(f"Connected to database: {record[0]}")
            cursor.close()
            conn.close()
            return True
    return False

if __name__ == "__main__":
    # Test the connection when running this file directly
    print("Testing database connection...")
    if test_connection():
        print("✅ Connection test successful!")
    else:
        print("❌ Connection test failed!")