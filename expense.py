import streamlit as st
import database as db
from datetime import datetime

def add_expense(user):
    if 'expense_data' not in st.session_state:
        st.session_state.expense_data = {}

    if 'expense_date' not in st.session_state:
        st.session_state.expense_date = None 
    
    st.write('<p style="color: green; border-bottom: 1px solid white; margin-top: -50px; font-size: 30px; font-weight: bold">Add Expense</p>', unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])
    with c1.container(border=True):
        placeholder=st.empty() 
        amount = st.number_input("Amount", min_value=0.0, step=100.0, format="%.2f")
        selected_date = st.date_input("Date", max_value=datetime.today())
        st.session_state.expense_date = selected_date
        category_options=db.get_all("Select head from expense_head",placeholder)
        category=[opt[0] for opt in category_options]
        category.append('Other')
        selected_category=' '
        if 'selected_other' not in st.session_state:
            st.session_state.selected_other = False
        def change_selected_other():
            st.session_state.selected_other=False
        selected_category = st.selectbox("Category", options=category, on_change=change_selected_other)
        if selected_category == "Other":
            selected_category = st.text_input("Enter Custom Category")
            if selected_category is not None and selected_category!='':
                st.session_state.selected_other = True
                selected_category=selected_category.strip()        
        if st.button("Add Expense"):
            if selected_category and amount:
                setattr(st.session_state, f"deduct{selected_category}", True)
                # Update session state with the new expense data
                if st.session_state.selected_other and selected_category.lower() in [i.lower() for i in category]:
                    st.session_state.selected_other=False
                    st.error("Category already exists.Please select it from category")
                else:
                    if selected_category not in st.session_state.expense_data and selected_category !='':
                        if selected_category.lower() in [i.lower() for i in st.session_state.expense_data.keys()]:
                            st.error("Category already included.Please first save expense to add in this category.")
                        else:
                            st.session_state.expense_data[selected_category] = 0.0
                            st.session_state.expense_data[selected_category] += amount
                        st.session_state.selected_other=False
                    else:
                        st.session_state.expense_data[selected_category] += amount
                        st.session_state.selected_other=False
            else:
                st.error("Please fill in both category and amount.")
    
    with c2.container(border=True):
        st.write(f'<p style="color: blue; border-bottom: 1px solid white; font-size: 20px; font-weight: bold">Your Expenses: {st.session_state.expense_date}</p>', unsafe_allow_html=True)
        s1, s2 = st.columns(2)
        s1.write(f'<p style="color: black; font-size: 18px; margin-bottom: -5px; text-align: left ">Category</p>', unsafe_allow_html=True)
        s2.write(f'<p style="color: black; font-size: 18px; margin-bottom: -5px; text-align: right ">Amount</p>', unsafe_allow_html=True)
        st.write('<hr style=" margin-top: 0px; margin-bottom: 0px">', unsafe_allow_html=True)
        cs1, cs2 = st.columns(2)
        total_expense=0
        for category, expense in st.session_state.expense_data.items():
            cs1.write(f'<p style="color: black; font-size: 15px; margin-bottom: 5px;text-align: left; margin-top: -5px">{category}</p>', unsafe_allow_html=True)
            cs2.write(f'<p style="color: black; font-size: 15px; margin-bottom: 5px;text-align: right;margin-top: -5px ">{expense}</p>', unsafe_allow_html=True)
            total_expense+=float(expense)
        
        cs1.write(f'<p style="color: black; font-size: 15px; margin-bottom: 5px;text-align: left; margin-top: -5px">Total Expense: </p>', unsafe_allow_html=True)
        cs2.write(f'<p style="color: black; font-size: 15px; margin-bottom: 5px;text-align: right;margin-top: -5px ">{total_expense}</p>', unsafe_allow_html=True)
        st.write('')
        if st.button("Save Expenses", key='save to db',use_container_width=True):
            conn = db.db_connect()
            cursor = conn.cursor()
            existing_categories = [opt[0] for opt in category_options]
            if selected_category.lower() not in [cat.lower() for cat in existing_categories]:
                cursor.execute("INSERT INTO expense_head (head) VALUES (%s)", (selected_category,))
                conn.commit()
            cursor.execute("SELECT amount, category FROM expenses WHERE date = %s AND username = %s", (st.session_state.expense_date, user))
            existing_records = cursor.fetchall()
            for category,amount in st.session_state.expense_data.items():    
                for existing_amount,existing_category in existing_records:
                    if category.lower() == existing_category.lower():
                        new_amount = existing_amount + amount    
                        cursor.execute("UPDATE expenses SET amount = %s WHERE date = %s AND category = %s AND username = %s", (new_amount, st.session_state.expense_date, category, user))
                        break
                else:
                    cursor.execute("INSERT INTO expenses (amount, date, category, username) VALUES (%s, %s, %s, %s)", (amount, st.session_state.expense_date, category, user))
                if 'expense_data' in st.session_state:
                    del st.session_state['expense_data']
            conn.commit()
            conn.close()
            # st.rerun()
    
    #This is to show user previous stored data of that date 
    with c2.container(border=True):
        st.write(f'<p style="color: blue; border-bottom: 1px solid white; font-size: 20px; font-weight: bold">Your Previous Expense: {st.session_state.expense_date}</p>', unsafe_allow_html=True)
        s1, s2 = st.columns(2)
        s1.write(f'<p style="color: black; font-size: 18px; margin-bottom: -5px; text-align: left ">Category</p>', unsafe_allow_html=True)
        s2.write(f'<p style="color: black; font-size: 18px; margin-bottom: -5px; text-align: right ">Amount</p>', unsafe_allow_html=True)
        st.write('<hr style=" margin-top: 0px; margin-bottom: 0px">', unsafe_allow_html=True)
        cs1, cs2 = st.columns(2)
        conn=db.db_connect()
        cursor=conn.cursor()       
        cursor.execute(f"select amount,category from expenses where date='{st.session_state.expense_date}' and username='{user}'   ") 
        store=cursor.fetchall()
        total_expense=0
        for expense, category in store:
            cs1.write(f'<p style="color: black; font-size: 15px; margin-bottom: 5px;text-align: left; margin-top: -5px">{category}</p>', unsafe_allow_html=True)
            cs2.write(f'<p style="color: black; font-size: 15px; margin-bottom: 5px;text-align: right;margin-top: -5px ">{expense}</p>', unsafe_allow_html=True)
            total_expense+=float(expense)
        
        cs1.write(f'<p style="color: black; font-size: 15px; margin-bottom: 5px;text-align: left; margin-top: -5px">Total : </p>', unsafe_allow_html=True)
        cs2.write(f'<p style="color: black; font-size: 15px; margin-bottom: 5px;text-align: right;margin-top: -5px ">{total_expense}</p>', unsafe_allow_html=True)
        st.write('')

if __name__ == "__main__":
    # add_expense(user)
    pass 