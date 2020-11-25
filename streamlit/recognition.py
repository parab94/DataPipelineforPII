import loginstatus,streamlit as st
import requests
import json
# from loginstatus import USERLOGINSTATUS

def app():
    st.title('Entity Identification')
    st.write('Welcome to the Enity Recognition page')

    #para = st.text_input("enter token here", value='', max_chars=None)
    CONTENT = "abel12345678901"
    if st.button('Identify Entities'):
        #st.write('Why hello there')
        if loginstatus.status == True:
            #res = requests.get(f"http://127.0.0.1:8000/comprehend")
            res = requests.get(f"https://h7xbsv1m5l.execute-api.us-east-1.amazonaws.com/prod/comprehend")
            st.write('Comprehension successful')
            st.write(res.json())
        else:
            st.write("please authenticate user and try again")