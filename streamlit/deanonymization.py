import requests,loginstatus,streamlit as st
# from loginstatus import USERLOGINSTATUS

def app():
    st.title('De-Anonymization')
    st.write('Welcome to the De-anonymization page')
    Hash = st.text_input("enter Hash here", value='', max_chars=None)
    filename = st.text_input("enter filename here", value='', max_chars=None)

    CONTENT = "abel12345678901"
    if st.button('De-Anonymize Data'):
        if loginstatus.status == True:  
            #res = requests.get(f"http://127.0.0.1:8000/reIdentifyEntities?Hash={Hash}&filename={filename}")
            res = requests.get(f"https://h7xbsv1m5l.execute-api.us-east-1.amazonaws.com/prod/reIdentifyEntities?Hash={Hash}&filename={filename}")
            st.write('Deanonymization successful')
            st.write(res.json())
        else:
            st.write("please authenticate user and try again")