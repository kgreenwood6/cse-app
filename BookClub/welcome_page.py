import streamlit as st
from streamlit_extras.switch_page_button import switch_page
st.set_page_config(initial_sidebar_state="collapsed")


# Clear the session state variables
keys = list(st.session_state.keys())
for key in keys:
    st.session_state.pop(key)


# Define the genre options available
genre_options = ['history', 'paranormal', 'crime', 'thriller', 'historical fiction', 'romance',
                 'graphic', 'non-fiction', 'fantasy', 'mystery', 'children', 'poetry', 'young-adult',
                 'comics', 'biography', 'fiction']


st.write('#### Welcome to Book Club! :books:')
st.text("")

st.write("##### Please select your genre preference(s) for receiving recommendations :male-detective:")
st.text("")

st.markdown('Select up to **three** genres')
selected_genres = st.multiselect(label='Select up to three genres',
                                 options=genre_options,
                                 label_visibility='collapsed',
                                 placeholder='Search for a genre ...')
st.text("")

# Create a button on the right hand side
col11, col12 = st.columns([0.9, 0.1])
with col12:
    next_button = st.button('Next')

# Define logic if button is pressed
if next_button:
    if len(selected_genres) == 0:
        st.error('Please select at least one genre!', icon="🚨")
    elif len(selected_genres) > 3:
        st.error('Please select a maximum of 3 genres!', icon="🚨")
    else:
        st.session_state['genres'] = selected_genres
        switch_page('liked')
