import loginstatus,streamlit as st
import requests
import json
import loginstatus

TOKEN =  ""
TOKEN2 = ""
URL = "http://seekingalpha.com/earnings/earnings-call-transcripts"
def app():
    st.title('Scraping')
    st.write('Welcome to the Scraping page')

    input_url = st.text_input("enter token here", value='', max_chars=None)
    CONTENT = "abel12345678901"
    if st.button('Scrape Data'):
        if loginstatus.status == True:
            if (input_url == URL):
                # st.write('Why hello there')
                #st.write(USERLOGINSTATUS)
                #res = requests.get(f"http://127.0.0.1:8000/scrapeCallTranscripts?url={input_url}")
                res = requests.get(f"https://h7xbsv1m5l.execute-api.us-east-1.amazonaws.com/prod/scrapeCallTranscripts?url={input_url}")
                # st.write('almost there')
                # st.write(res.json())
                st.write("Scraping Successful")
            else:
                st.write(loginstatus.status)
                st.write("Please enter correct URL")
        else:
            st.write("please authenticate user and try again")
# http://127.0.0.1:8000/secure_endpoint?access_token=dsfadsfsdf


    