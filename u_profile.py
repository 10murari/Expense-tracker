import streamlit as st 
import base64  # for image
import database as db 
import bcrypt  # for password hasing
import binascii

def main(user):
    st.write('<p style="color: green; border-bottom: 1px solid white; margin-top: -50px; font-size: 30px;text-align: center; font-weight: bold">Your Profile</p>', unsafe_allow_html=True)

    c1,c2,c3=st.columns([1,2.5,1])
    with c2.container(border=True):
        placeholder=st.empty() 
        user_detail=db.get_one(f"select name,username,image,password_hash from users where username='{user}'",placeholder)
        st.write(f"""<div style='margin-top: 10px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; height: 100%;'>
                <img src="data:image/png;base64,{base64.b64encode(user_detail[2]).decode()}"  width="150" height="150" style="margin-bottom: 20px; border-radius: 100%; object-fit: cover;"  />
                <p style='margin-bottom: 0px; margin-top: -20px; font-size: 20px;  color:black; font-weight: bold'>{user_detail[0]}</p>
                <p style='margin-bottom: 2px; font-size: 15px; color: grey; '>{user_detail[1]}</p>   
                <br><br>
                """,unsafe_allow_html=True)
        st.write(f"""<div style='margin-top: -10px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; height: 100%;'>
                <p style='margin-bottom: 0px; margin-top: -0px; font-size: 20px;  color:green; font-weight: bold'>Update Details</p>
                """,unsafe_allow_html=True)
        with st.form('ChangeDetail',clear_on_submit=False):
            old_pwd=str(st.text_input('Old Password',key='p_old'))
            new_pwd=str(st.text_input('New Password',key='p_new'))
            confirm=str(st.text_input('Confirm New Password',key='c_new'))
            image=st.file_uploader('Change Profile Picture',type=['jpg','jpeg','png'])
            

            if st.form_submit_button('Update details'):
                place = st.empty()
                if old_pwd.strip() or new_pwd.strip() or confirm.strip():
                    # if new_pwd.strip() and confirm.strip():
                    # Check if old password matches the stored hashed password
                        if bcrypt.checkpw(old_pwd.encode(), binascii.unhexlify(user_detail[3])):
                            if new_pwd == confirm:
                                # Update password in the database
                                # db.update_password(user, new_pwd,slot=place,msg="Password updated successfully")
                                db.update_password(user, new_pwd)
                                place.success("Password updated Successfully")
                                
                            else:
                                place.error('New password and confirmation do not match')
                        else:
                            place.error('Old password is incorrect')
                    

                if image:
                    # Update profile picture in the database
                    
                    db.update_profile_picture(user, image.read(),place,msg="Profile Image Updated")
                    # place.success('Profile picture updated successfully')
                elif not image and not (old_pwd.strip() and new_pwd.strip() and confirm.strip()):
                    place.error('No Details to update')

if __name__=='__main__':
    pass 




