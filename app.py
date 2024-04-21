import streamlit as st 
import database as db 
from streamlit_option_menu import option_menu
import base64
import time 
import psycopg2
import u_profile as profile 
import income
import expense 
import report

st.set_page_config(
    page_title='Expense-Tracker',
    layout='wide'
)

if 'loggedin_user' not in st.session_state:
    st.session_state.loggedin_user=None  

def logout():
    st.session_state.loggedin=False 

def logo():
    image_path='icons\\icon.png'
    with open(image_path,'rb') as img:
        image=img.read() 
    st.write(f"""<div style='margin-top: -45px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; height: 100%;'>
            <img src="data:image/png;base64,{base64.b64encode(image).decode()}"  width="150" height="150" style="margin-bottom: 10px; border-radius: 0%; object-fit: cover;"  />
            <p style='margin-bottom:     
            """,unsafe_allow_html=True)
    st.write("<p style='font-weight: bold; font-size: 30px; text-align: center; color: green'> Expense Tracker </p>",unsafe_allow_html=True)

def signup():
    with st.form("Signup Form",clear_on_submit=True,border=True):
        name=st.text_input('Full Name:',label_visibility='collapsed',placeholder='Full Name')
        username=st.text_input('UserName:',label_visibility='collapsed',placeholder='Username',key='s_up_u')
        password=st.text_input('Passsword:',type='password',label_visibility='collapsed',placeholder='Password',key='s_up_p')
        image=st.file_uploader('Profile Image',type=['jpg','jpeg','png'])
        if st.form_submit_button('Sign Up'):
            placeholder=st.empty()
            if db.check_user_existence(username):
                placeholder.error('Username already Used')
            else:
                if(image):
                        image=image.read() 
                else:
                    image_path = 'icons/def_icon.png'
                    with open(image_path, 'rb') as file:
                        image = file.read()
                if name.strip() and username.strip() and password.strip():
                    hash_pw=db.hash_generator(password)
                    db.insert_db(f"insert into users(username, password_hash,name,image) values('{username}','{hash_pw}','{name}',{psycopg2.Binary(image)})",place=placeholder,msg='User Registered')
                else:
                    placeholder.error('All field required')
                time.sleep(3)
                placeholder.empty() 
                st.rerun()

def landing_page():
    with st.sidebar:
        logo()
        selected=option_menu(
            orientation="vertical",menu_title='',
            options=['Profile','Income','Expense','Report'],
            styles={
        "container": {"padding": "0!important", "background-color": "#6AF624"},
        "icon": {"color": "black", "font-size": "30px"}, 
        "nav-link": {"font-size": "15px", "text-align": "justify", "margin":"0px","margin-top": "0px", "--hover-color": "#558B9A"},
        "nav-link-selected": {"background-color": " #0DA2CC"}},
        icons=['person','wallet','cart','chat-square-dots-fill'],key='options')
        st.button('Log Out',on_click=logout,use_container_width=True)

    return selected

def main():
    if 'loggedin' not in st.session_state:
        st.session_state.loggedin=False 

    if st.session_state.loggedin==False:
        c1,c2,c3=st.columns([1,1.5,1])
        with c2:
            logo()
            s1,s2,s3=st.columns([1.5,2,1])
            opt=s2.radio('label',options=['Login','Sign Up'],index=0,horizontal=True,label_visibility='collapsed')

            if opt=='Login':
                with st.container(border=True):
                    place1=st.empty() 
                    username=place1.text_input('UserName:',label_visibility='collapsed',placeholder='Username')
                    place2=st.empty() 
                    password=place2.text_input('Passsword:',type='password',label_visibility='collapsed',placeholder='Password')
                    place3=st.empty() 
                    if place3.button('Login'):
                        placeholder=st.empty()
                        db_pwd=db.get_one(f"Select password_hash from users where username='{username}'",placeholder)
                        if db_pwd:
                            if db.check_pw(password,db_pwd[0]):
                                placeholder.success('Logged In')
                                st.session_state.loggedin_user=username
                                st.session_state.loggedin=True
                                place1.empty()
                                place2.empty()
                                place3.empty()
                                st.rerun() 
                            else:
                                placeholder.error('Invalid Password')
                        else:
                            placeholder.error('User Not Found')
                        time.sleep(3)
                        placeholder.empty() 
            else:
                signup()

    if st.session_state.loggedin:
        return landing_page() 

if __name__=='__main__':
    selected=main()
    if selected=='Profile':
        # st.write(st.session_state.loggedin_user)
        profile.main(st.session_state.loggedin_user) 
    if selected=='Income':
        income.add_income_record(st.session_state.loggedin_user)
    if selected=='Expense':
        expense.add_expense(st.session_state.loggedin_user)
    if selected=='Report':
        report.show_menu()