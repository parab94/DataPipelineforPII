import streamlit as st
import scraping, masking, deanonymization, recognition, login, loginstatus 
import requests

def app():
    st.title('Login Page')
    st.write('Welcome to the login page')

    username = st.text_input("User Name", value='', max_chars=None)
    password = st.text_input("Password", value='', max_chars=None)

    if st.button('Login Now'):
        # st.write(username)
        # st.write(password)
        # # st.write(loginstatus.status)
        res = requests.get(f"https://h7xbsv1m5l.execute-api.us-east-1.amazonaws.com/prod/authenticate?username={username}&password={password}")
        #res = requests.get(f"http://127.0.0.1:8000/authenticate?username={username}&password={password}")
        result = res.json()
        message = ""
        result = str(result)
        if result == "True":
            loginstatus.status = True
            message = "Authenticated Successfully"
            st.balloons()
        
        else:
            loginstatus.status = False
            message = "Not Authenticated"

        st.header(message)
