import streamlit as st
from streamlit_extras.switch_page_button import switch_page


# Create layout of streamlit page
st.write("##### Thank you for using Book Club! :white_check_mark:")
st.text("")

another_rec = st.button("Get another recommendation!", type='primary')

if another_rec:
    switch_page('welcome_page')
