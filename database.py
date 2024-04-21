import psycopg2
import bcrypt
import binascii
from datetime import datetime, timedelta
import streamlit as st

DATABASE_CONFIG={
    'database':'expense',
    'user':'postgres',
    'password':'admin',
    'host':'localhost',
    'port':'5432'
}

def db_connect():
    conn=psycopg2.connect(**DATABASE_CONFIG)
    return conn 

def get_one(query,place):
    '''
    Function to fetch single tuple from database. 

    Parameters:
        query: Any valid sql query 
        place: plaeholder (st.empty) to display the message 

    Returns:
        Output tuple. 
    '''
    conn=db_connect() 
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            result=cur.fetchone()
    except (Exception,psycopg2.DatabaseError) as error:
         place.error(error)
    finally:
        if conn is not None:
            cur.close() 
            conn.close() 
        return result

def get_all(query,place):
    '''
    Function to fetch all tuple from database. 

    Parameters:
    query: Any valid sql query 
    place: plaeholder (st.empty) to display the message 

    Returns:
    Output tuple. 
    '''
    conn=db_connect() 
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            result=cur.fetchall()
    except (Exception,psycopg2.DatabaseError) as error:
         place.error(error)
    finally:
        if conn is not None:
            cur.close() 
            conn.close() 
        return result

def insert_db(query,place,msg=None):
    '''
    Function to add tuple to database. 

    Parameters:
    query: Any valid sql query 
    place: plaeholder (st.empty) to display the message 
    msg: Msg to display
    
    Returns:
    None  
    '''
    conn=db_connect() 
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            conn.commit() 
            if msg is not None:
                place.success(msg)
    except (Exception,psycopg2.DatabaseError) as error:
         place.error(error)
    finally:
        if conn is not None:
            cur.close() 
            conn.close()  

def hash_generator(password):
    password_hash=bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    password_hashed=binascii.hexlify(password_hash).decode('utf-8')
    return password_hashed

def check_pw(password,db_pwd):
    return bcrypt.checkpw(password.encode(),binascii.unhexlify(db_pwd))

# Function to update user's password
def update_password(username, new_password):
    conn = db_connect()
    try:
        with conn.cursor() as cur:
            # Generate bcrypt hash for the new password
            password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
            password_hashed = binascii.hexlify(password_hash).decode('utf-8')

            # Update the password in the database
            cur.execute("UPDATE users SET password_hash = %s WHERE username = %s", (password_hashed, username))
            conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error updating password:", error)
    finally:
        if conn is not None:
            conn.close()

# Function to update user's profile picture
def update_profile_picture(username, new_image,slot,msg=None):
    conn = db_connect()
    try:
        with conn.cursor() as cur:
            # Update the profile picture in the database
            cur.execute("UPDATE users SET image = %s WHERE username = %s", (psycopg2.Binary(new_image), username))
            conn.commit()
            if msg:
                slot.success(msg)
    except (Exception, psycopg2.DatabaseError) as error:
        slot.error(f"Error updating profile picture:{error}")
    finally:
        if conn is not None:
            conn.close()

# # for income section
# def insert_income_record(amount, date, category, description):
#     conn = db_connect()
#     try:
#         with conn.cursor() as cur:
#             cur.execute("INSERT INTO income (amount, date, category, description) VALUES (%s, %s, %s, %s)",
#                         (amount, date, category, description))
#             conn.commit()
#     except (Exception, psycopg2.DatabaseError) as error:
#         print("Error inserting income record:", error)
#     finally:
#         if conn is not None:
#             conn.close()
 
# # this is for expense section
# def insert_expense_record(amount, date, category, description):
#     conn = db_connect()
#     try:
#         with conn.cursor() as cur:
#             cur.execute("INSERT INTO expenses (amount, date, category, description) VALUES (%s, %s, %s, %s)",
#                         (amount, date, category, description))
#             conn.commit()
#     except (Exception, psycopg2.DatabaseError) as error:
#         print("Error inserting expense record:", error)
#     finally:
#         if conn is not None:
#             conn.close()

# def get_total_expenses(date):
#     conn = db_connect()
#     try:
#         with conn.cursor() as cur:
#             cur.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE date = %s", (date,))
#             total_expenses = cur.fetchone()[0]
#             return total_expenses if total_expenses is not None else 0
#     except (Exception, psycopg2.DatabaseError) as error:
#         print("Error fetching total expenses:", error)
#         return 0
#     finally:
#         if conn is not None:
#             conn.close()


# def get_category_expense(date, category):
#     conn = db_connect()
#     try:
#         with conn.cursor() as cur:
#             cur.execute("SELECT SUM(amount) FROM expenses WHERE date = %s AND category = %s", (date, category))
#             category_expense = cur.fetchone()[0]
#             return category_expense if category_expense is not None else 0
#     except psycopg2.Error as e:
#         print("Error fetching category expense:", e)
#         return 0
#     finally:
#         conn.close()

# def get_total_category_expenses(date):
#     conn = db_connect()
#     total_category_expenses = {}
#     try:
#         with conn.cursor() as cur:
#             cur.execute("SELECT category, SUM(amount) FROM expenses WHERE date = %s GROUP BY category", (date,))
#             rows = cur.fetchall()
#             for row in rows:
#                 category, total_expense = row
#                 total_category_expenses[category] = total_expense
#     except psycopg2.Error as e:
#         print("Error fetching total category expenses:", e)
#     finally:
#         conn.close()
#     return total_category_expenses



# def get_income_trend(start_date=None, end_date=None):
#     conn = db_connect()
#     try:
#         with conn.cursor() as cur:
#             if not start_date or not end_date:
#                 # Default to last 30 days
#                 start_date = datetime.today() - timedelta(days=30)
#                 end_date = datetime.today()
#             cur.execute("SELECT date, amount FROM income WHERE date BETWEEN %s AND %s", (start_date, end_date))
#             income_data = cur.fetchall()
#     except psycopg2.Error as e:
#         print("Error fetching income trend data:", e)
#         income_data = []
#     finally:
#         conn.close()
#     return income_data

# def get_expense_trend(start_date=None, end_date=None):
#     conn = db_connect()
#     try:
#         with conn.cursor() as cur:
#             if not start_date or not end_date:
#                 # Default to last 30 days
#                 start_date = datetime.today() - timedelta(days=30)
#                 end_date = datetime.today()
#             cur.execute("SELECT date, amount FROM expenses WHERE date BETWEEN %s AND %s", (start_date, end_date))
#             expense_data = cur.fetchall()
#     except psycopg2.Error as e:
#         print("Error fetching expense trend data:", e)
#         expense_data = []
#     finally:
#         conn.close()
#     return expense_data

# def get_expense_distribution():
#     conn = db_connect()
#     try:
#         with conn.cursor() as cur:
#             cur.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
#             expense_distribution = cur.fetchall()
#     except psycopg2.Error as e:
#         print("Error fetching expense distribution data:", e)
#         expense_distribution = []
#     finally:
#         conn.close()
#     return expense_distribution

#------------------PratikTheGod-----------------
def check_user_existence(username:str): 
    """This function check if username already exists or not\n
    Args:
        username: User's username
    Return:
        It returns true if username already exists in database otherwise false
    """
    try:
        con=db_connect()
        cursor=con.cursor()
        cursor.execute("select * from users where username=%s",(username,))
        result=cursor.fetchone()
        if result:
            return True
        else:
            return False
    except (Exception, psycopg2.DatabaseError) as error:
        st.error(error)
    finally:
        if con is not None:
            con.close()