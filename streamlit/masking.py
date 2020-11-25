import loginstatus,requests,json,streamlit as st

# from loginstatus import USERLOGINSTATUS

def app():
    st.title('Masking')
    st.write('Welcome to the Masking page')
    ExeName = st.text_input("enter ExeName here", value='', max_chars=None)
    keyname = st.text_input("enter keyname here", value='', max_chars=None)
    
    CONTENT = "abel12345678901"
    if st.button('Mask Data') :
        if loginstatus.status == True:
            st.write('Why hello there')
            print(loginstatus.status)
            #res = requests.get(f"http://127.0.0.1:8000/de-identify?ExeName={ExeName}&keyname={keyname}")
            res = requests.get(f"https://h7xbsv1m5l.execute-api.us-east-1.amazonaws.com/prod/de-identify?ExeName={ExeName}&keyname={keyname}")
            st.write('masking successful')
            st.write(res.json())
        else:
            st.write("please authenticate user and try again")