import streamlit as st
import database as db
from datetime import datetime

def add_income_record(user):
    if 'income_data' not in st.session_state:
        st.session_state.income_data = {}

    if 'income_date' not in st.session_state:
        st.session_state.income_date = None 

    st.write('<p style="color: green; border-bottom: 1px solid white; margin-top: -50px; font-size: 30px;text-align: center;font-weight: bold">Add income</p>', unsafe_allow_html=True)
    
    c1,c2=st.columns([2,1])
    with c1.container(border=True):
        # Input fields for income information
        placeholder=st.empty() 
        # amt_placeholder=st.empty()
        amount = st.number_input("Amount", min_value=0.0, step=100.0, format="%.2f")
        selected_date = st.date_input("Date", max_value=datetime.today())
        st.session_state.income_date = selected_date
        category_options=db.get_all("Select head from income_head",placeholder)
        category=[opt[0] for opt in category_options]
        category.append('Other')
        selected_category=' '
        if 'selected_other' not in st.session_state:
            st.session_state.selected_other = False
        def change_selected_other():
            st.session_state.selected_other=False
        selected_category = st.selectbox("Category", options=category, on_change=change_selected_other)
        if selected_category == "Other":
            #st.session_state.selected_other is to know whether user selected "other" or not
            selected_category = st.text_input("Other Category")
            if selected_category is not None and selected_category!="" :
                st.session_state.selected_other = True
                selected_category=selected_category.strip() 
        if st.button("Add income"):
            if selected_category and amount:
                setattr(st.session_state, f"increase{selected_category}", True)
                if st.session_state.selected_other and selected_category.lower() in [i.lower() for i in category]:
                    st.session_state.selected_other=False
                    st.error("Category already exists.Please select it from category")
                else:
                    if selected_category not in st.session_state.income_data and selected_category !='':
                        if selected_category.lower() in [i.lower() for i in st.session_state.income_data.keys()]:
                            st.error("Category already included.Please first save income to add in this category.")
                        else:
                            st.session_state.income_data[selected_category] = 0.0
                            st.session_state.income_data[selected_category] += amount
                        st.session_state.selected_other=False
                    else:
                        st.session_state.income_data[selected_category] += amount
                        st.session_state.selected_other=False
            else:
                st.error("Please fill in both category and amount.")

    with c2.container(border=True):
        st.write(f'<p style="color: blue; border-bottom: 1px solid white; font-size: 20px; font-weight: bold">Your Income: {st.session_state.income_date}</p>', unsafe_allow_html=True)
        s1, s2 = st.columns(2)
        s1.write(f'<p style="color: black; font-size: 18px; margin-bottom: -5px; text-align: left ">Category</p>', unsafe_allow_html=True)
        s2.write(f'<p style="color: black; font-size: 18px; margin-bottom: -5px; text-align: right ">Amount</p>', unsafe_allow_html=True)
        st.write('<hr style=" margin-top: 0px; margin-bottom: 0px">', unsafe_allow_html=True)
        cs1, cs2 = st.columns(2)
        total_income=0
        for category,income in st.session_state.income_data.items():
            cs1.write(f'<p style="color: black; font-size: 15px; margin-bottom: 5px;text-align: left; margin-top: -5px">{category}</p>', unsafe_allow_html=True)
            cs2.write(f'<p style="color: black; font-size: 15px; margin-bottom: 5px;text-align: right;margin-top: -5px ">{income}</p>', unsafe_allow_html=True)
            total_income+=float(income)
        
        cs1.write(f'<p style="color: black; font-size: 15px; margin-bottom: 5px;text-align: left; margin-top: -5px">Total : </p>', unsafe_allow_html=True)
        cs2.write(f'<p style="color: black; font-size: 15px; margin-bottom: 5px;text-align: right;margin-top: -5px ">{total_income}</p>', unsafe_allow_html=True)
        st.write('')
        if st.button("Save Income", key='save_to_db',use_container_width=True):
            if not st.session_state.income_data:
                st.warning("Add at least one income entry before saving.")
            else:
                conn = db.db_connect()
                try:
                    with conn.cursor() as cursor:
                        existing_categories_lower = {opt[0].lower() for opt in category_options}
                        for category_name in st.session_state.income_data.keys():
                            if category_name.lower() not in existing_categories_lower:
                                cursor.execute("INSERT INTO income_head (head) VALUES (%s)", (category_name,))
                                existing_categories_lower.add(category_name.lower())

                        cursor.execute(
                            "SELECT amount, category FROM income WHERE date = %s AND username = %s",
                            (st.session_state.income_date, user)
                        )
                        existing_records = {
                            existing_category.lower(): (existing_amount, existing_category)
                            for existing_amount, existing_category in cursor.fetchall()
                        }

                        for category_name, amount in st.session_state.income_data.items():
                            if category_name.lower() in existing_records:
                                existing_amount, existing_category_name = existing_records[category_name.lower()]
                                new_amount = existing_amount + amount
                                cursor.execute(
                                    "UPDATE income SET amount = %s WHERE date = %s AND category = %s AND username = %s",
                                    (new_amount, st.session_state.income_date, existing_category_name, user)
                                )
                            else:
                                cursor.execute(
                                    "INSERT INTO income (amount, date, category, username) VALUES (%s, %s, %s, %s)",
                                    (amount, st.session_state.income_date, category_name, user)
                                )
                    conn.commit()
                finally:
                    conn.close()
                st.session_state.income_data = {}
                st.success("Income saved successfully.")
                st.rerun()

    #This is to show user previous stored data of that date 
    with c2.container(border=True):
        st.write(f'<p style="color: blue; border-bottom: 1px solid white; font-size: 20px; font-weight: bold">Your Previous Income: {st.session_state.income_date}</p>', unsafe_allow_html=True)
        s1, s2 = st.columns(2)
        s1.write(f'<p style="color: black; font-size: 18px; margin-bottom: -5px; text-align: left ">Category</p>', unsafe_allow_html=True)
        s2.write(f'<p style="color: black; font-size: 18px; margin-bottom: -5px; text-align: right ">Amount</p>', unsafe_allow_html=True)
        st.write('<hr style=" margin-top: 0px; margin-bottom: 0px">', unsafe_allow_html=True)
        cs1, cs2 = st.columns(2)
        conn=db.db_connect()
        cursor=conn.cursor()       
        cursor.execute(
            "select amount,category from income where date=%s and username=%s",
            (st.session_state.income_date, user)
        ) 
        store=cursor.fetchall()
        total_income=0
        for income, category in store:
            cs1.write(f'<p style="color: black; font-size: 15px; margin-bottom: 5px;text-align: left; margin-top: -5px">{category}</p>', unsafe_allow_html=True)
            cs2.write(f'<p style="color: black; font-size: 15px; margin-bottom: 5px;text-align: right;margin-top: -5px ">{income}</p>', unsafe_allow_html=True)
            total_income+=float(income)
        
        cs1.write(f'<p style="color: black; font-size: 15px; margin-bottom: 5px;text-align: left; margin-top: -5px">Total : </p>', unsafe_allow_html=True)
        cs2.write(f'<p style="color: black; font-size: 15px; margin-bottom: 5px;text-align: right;margin-top: -5px ">{total_income}</p>', unsafe_allow_html=True)
        st.write('')
        conn.close()

if __name__ == "__main__":
    pass
