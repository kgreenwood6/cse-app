import re
import toml
import psycopg2
import streamlit as st
from streamlit_searchbox import st_searchbox
from streamlit_extras.switch_page_button import switch_page


# Clear the session state variables
keys = ['disliked_bookid_1', 'disliked_bookid_2', 'disliked_bookid_3', 'disliked_bookid_4', 'disliked_bookid_5']
for key in keys:
    if key in st.session_state:
        st.session_state.pop(key)


# Get the database connection engine object
@st.cache_resource
def get_db_engine():
    # Load the TOML file
    db_config = toml.load("secrets.toml")

    # Connect to Postgres DB using info from TOML file
    db_conn = psycopg2.connect(
        host=db_config['database']['host'],
        port=db_config['database']['port'],
        dbname=db_config['database']['name'],
        user=db_config['database']['user'],
        password=db_config['database']['password']
    )

    # Get the cursor object
    db_cursor = db_conn.cursor()

    # Return the database connection and cursor objects
    return db_conn, db_cursor


conn, cursor = get_db_engine()
genres = st.session_state['genres']
num_genres = len(st.session_state['genres'])


def get_search_titles(search_term, cursor_arg, genres_arg, num_genres_arg, limit=20):
    if num_genres_arg == 1:
        query = """SELECT title, author_names, book_id
                   FROM english_books
                   WHERE search_title @@ plainto_tsquery('english',  '%s')
                   AND genres LIKE '%s'
                   LIMIT %s""" % (f"%{search_term}%", f"%{genres_arg[0]}%", limit)
    elif num_genres_arg == 2:
        query = """SELECT title, author_names, book_id
                   FROM english_books
                   WHERE search_title @@ plainto_tsquery('english',  '%s')
                   AND (genres LIKE '%s' OR genres LIKE '%s')
                   LIMIT %s""" % (f"%{search_term}%", f"%{genres_arg[0]}%", f"%{genres_arg[1]}%", limit)
    else:
        query = """SELECT title, author_names, book_id
                   FROM english_books
                   WHERE search_title @@ plainto_tsquery('english',  '%s')
                   AND (genres LIKE '%s' OR genres LIKE '%s' OR genres LIKE '%s')
                   LIMIT %s""" % (f"%{search_term}%", f"%{genres_arg[0]}%", f"%{genres_arg[1]}%", f"%{genres_arg[2]}%", limit)

    cursor_arg.execute(query)
    rows = cursor_arg.fetchall()

    # Create empty list to store search options
    returned_titles = [f'{row[0]} by {row[1]} ({row[2]})' for row in rows]

    # Return the search titles found
    return returned_titles


def search_titles(search_term):
    # Search function for streamlit-searchbox
    if search_term:
        filtered_titles = get_search_titles(search_term=search_term, cursor_arg=cursor, genres_arg=genres, num_genres_arg=num_genres, limit=20)
        return filtered_titles
    return []


def extract_book_id(input_string):
    match = re.search(r'\((\d+)\)$', input_string)
    if match:
        return match.group(1)
    else:
        return None


st.write("##### Please select up to 5 books which you disliked within your specified genre(s) :disappointed:")
st.text("")

# Add searchbar for first disliked book title
st.markdown('Select the title of your **first** disliked book')
disliked_book_1 = st_searchbox(
    search_function=search_titles,
    placeholder='Search for a title ...',
    key='search_box_6'
)

# Add searchbar for second disliked book title
st.markdown('Select the title of your **second** disliked book')
disliked_book_2 = st_searchbox(
    search_function=search_titles,
    placeholder='Search for a title ...',
    key='search_box_7')

# Add searchbar for third disliked book title
st.markdown('Select the title of your **third** disliked book')
disliked_book_3 = st_searchbox(
    search_function=search_titles,
    placeholder='Search for a title ...',
    key='search_box_8')

# Add searchbar for fourth disliked book title
st.markdown('Select the title of your **fourth** disliked book')
disliked_book_4 = st_searchbox(
    search_function=search_titles,
    placeholder='Search for a title ...',
    key='search_box_9')

# Add searchbar for fifth disliked book title
st.markdown('Select the title of your **fifth** disliked book')
disliked_book_5 = st_searchbox(
    search_function=search_titles,
    placeholder='Search for a title ...',
    key='search_box_10')

st.text("")

# Create button on the right hand side
col11, col12, col13 = st.columns([0.1, 0.6, 0.3])
with col11:
    back_button = st.button('Back')
with col13:
    next_button = st.button('Get Recommendations!', type='primary')

if back_button:
    switch_page('liked')
if next_button:
    if any([disliked_book_1, disliked_book_2, disliked_book_3, disliked_book_4, disliked_book_5]):
        if disliked_book_1:
            disliked_bookid_1 = extract_book_id(disliked_book_1)
            st.session_state['disliked_bookid_1'] = disliked_bookid_1
        if disliked_book_2:
            disliked_bookid_2 = extract_book_id(disliked_book_2)
            st.session_state['disliked_bookid_2'] = disliked_bookid_2
        if disliked_book_3:
            disliked_bookid_3 = extract_book_id(disliked_book_3)
            st.session_state['disliked_bookid_3'] = disliked_bookid_3
        if disliked_book_4:
            disliked_bookid_4 = extract_book_id(disliked_book_4)
            st.session_state['disliked_bookid_4'] = disliked_bookid_4
        if disliked_book_5:
            disliked_bookid_5 = extract_book_id(disliked_book_5)
            st.session_state['disliked_bookid_5'] = disliked_bookid_5
        switch_page('recommendations')
    else:
        st.error('Please select at least 1 disliked book!', icon="🚨")
