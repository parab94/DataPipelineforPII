import streamlit as st
import scraping, masking, deanonymization, recognition, login, loginstatus, anonymize, sentiment

PAGELIST = {
    "Login": login,
    "Scraping": scraping,
    "Recognition": recognition,
    "Masking": masking,
    # "Anonimization": anonymize,
    "Deanonymization": deanonymization,
    "Sentiment": sentiment
}

st.sidebar.title('Team 7')
selection_default = st.sidebar.radio("Please Login First", list(PAGELIST.keys()))
page = PAGELIST[selection_default]
page.app()
