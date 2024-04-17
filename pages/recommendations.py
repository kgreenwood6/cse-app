import toml
import requests
import psycopg2
import numpy as np
import streamlit as st
from bs4 import BeautifulSoup
from streamlit_extras.switch_page_button import switch_page
from collaborative_filtering_recommender import CollaborativeFiltering
import random


# Obtain the liked book IDs and store them in a list
liked_book_ids = []
for i in range(1, 6):
    if f'liked_bookid_{i}' in st.session_state:
        liked_book_ids.append(st.session_state[f'liked_bookid_{i}'])

# Obtain the disliked book IDs and store them in a list
disliked_book_ids = []
for i in range(1, 6):
    if f'disliked_bookid_{i}' in st.session_state:
        disliked_book_ids.append(st.session_state[f'disliked_bookid_{i}'])

# Obtain the genres
genres = st.session_state['genres']


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


# Define a function to load the CSS file
def load_css(file_name):
    with open(file_name) as f:
        css = f'<style>{f.read()}</style>'
    return css


# Load the external CSS file
css = load_css(file_name='stylesheet.css')
st.markdown(css, unsafe_allow_html=True)


# Define function to get recommended book IDs from content-based filtering
@st.cache_data
def get_content_recommendations(book_ids, genres_arg):

    # Create two empty lists to store the content-based and wildcard recs
    content_based_recs = []
    wildcard_recs = []

    for book_id in book_ids:
        # Get the genre and cluster for each liked book ID
        query = """SELECT genre, cluster
                   FROM kmeans_genre_clusters 
                   WHERE book_id = '%s'""" % book_id

        cursor.execute(query)
        row = cursor.fetchone()

        genre_val = row[0]
        cluster_val = row[1]

        # Get the content based recs from the same genre and cluster as the liked book
        query = """SELECT e.book_id
                   FROM kmeans_genre_clusters k INNER JOIN english_books e
                   ON CAST(k.book_id AS TEXT) = e.book_id
                   WHERE k.genre = '%s' AND k.cluster = '%s' AND k.book_id != '%s'
                   ORDER BY e.average_rating DESC, e.ratings_count DESC
                   LIMIT 5;
                """ % (genre_val, cluster_val, book_id)

        cursor.execute(query)
        rows = cursor.fetchall()
        content_based_recs.extend(rows)

        # Get the wildcard rec from the same genre and cluster as the liked book
        query = """SELECT e.book_id
                   FROM kmeans_genre_clusters k INNER JOIN english_books e
                   ON CAST(k.book_id AS TEXT) = e.book_id
                   WHERE k.genre = '%s' AND k.cluster = '%s' AND k.book_id != '%s'
                   ORDER BY e.ratings_count, e.average_rating DESC
                   LIMIT 5;
                """ % (genre_val, cluster_val, book_id)

        cursor.execute(query)
        rows = cursor.fetchall()
        wildcard_recs.extend(rows)

    content_based_recs = list(set(content_based_recs))
    wildcard_recs = list(set(wildcard_recs))
    content_based_recs = [rec[0] for rec in content_based_recs]
    wildcard_recs = [rec[0] for rec in wildcard_recs]
    content_based_recs = np.random.choice(content_based_recs, size=5, replace=False)
    wildcard_rec = np.random.choice(wildcard_recs, size=1, replace=False)
    return content_based_recs, wildcard_rec

@st.cache_data
def initialize_collaborative_filtering():
    cf = load_data_for_collaborative_filtering()
    return calculate_recommender_matrix(cf)


@st.cache_data
def calculate_recommender_matrix(cf):
    return cf.init_model()
    
@st.cache_data
def load_data_for_collaborative_filtering():
    return CollaborativeFiltering()

@st.cache_data
def get_collaborative_recommendations():
    cf = initialize_collaborative_filtering()
    return cf.get_all_recommendations(liked_book_ids, disliked_book_ids, 10)


# Define function to get book details from the book ID
@st.cache_data
def get_book_details(book_ids: list):

    book_details = []

    for book_id in book_ids:
        query = """SELECT title, author_names, image_url
                   FROM english_books 
                   WHERE book_id = '%s'""" % book_id

        cursor.execute(query)
        row = cursor.fetchone()
        title = row[0]
        author_names = row[1]
        image_url = row[2]

        if 'nophoto' in image_url:
            book_url = f'https://www.goodreads.com/book/show/{book_id}'
            response = requests.get(book_url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                try:
                    book_cover = soup.find("img", class_="ResponsiveImage")['src']
                except:
                    book_cover = None

                if book_cover is not None and book_cover != '':
                    image_url = book_cover

        book_details.append([title, author_names, image_url])

    return book_details


# Define function to store user feedback in the DB
def store_feedback(user_name_arg, feedback_1_arg, feedback_2_arg, feedback_3_arg,
                   feedback_4_arg, feedback_5_arg, feedback_wc_arg, ces_arg, nps_arg):

    cursor.execute("""SELECT MAX(id) FROM user_feedback;""")
    get_maximum_id = cursor.fetchone()
    if get_maximum_id[0] is None:
        put_maximum_id = 1
    else:
        put_maximum_id = get_maximum_id[0] + 1

    data = (put_maximum_id, user_name_arg, feedback_1_arg, feedback_2_arg, feedback_3_arg, feedback_4_arg, feedback_5_arg, feedback_wc_arg, ces_arg, nps_arg)
    cursor.execute(
        "INSERT INTO user_feedback (id, user_name, feedback_1, feedback_2, feedback_3, feedback_4, feedback_5, feedback_wc, CES, NPS) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        data)

    conn.commit()


# Get the book recommendations
content_recs, wildcard_rec = get_content_recommendations(book_ids=liked_book_ids, genres_arg=genres)
collaborative_recs, collaborative_wildcard_rec = get_collaborative_recommendations()

use_content_wildcard = random.choice([True, False])
if not use_content_wildcard:
    wildcard_rec = collaborative_wildcard_rec
    content_recs = content_recs[:3].extend(collaborative_recs[:2])
else:
    content_recs = content_recs[:2].extend(collaborative_recs[:3])

recommended_books = get_book_details(book_ids=content_recs)
wildcard_book = get_book_details(book_ids=wildcard_rec)


# Create layout of streamlit page
st.write("##### Please find below your **Book Club** recommendations :dizzy:")
st.text("")

col01, col02 = st.columns([0.69, 0.31])
with col02:
    st.markdown('Is **this** recommendation useful?')

col11, col12 = st.columns([0.69, 0.31])
with col11:
    rec_one = recommended_books[0]
    st.image(rec_one[2], width=100)
    st.markdown(f'<p class="title-font">{rec_one[0]}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="author-font">{rec_one[1]}</p>', unsafe_allow_html=True)
with col12:
    feedback_1 = st.radio(
        "Is this recommendation useful?",
        [":thumbsup:", ":thumbsdown:"],
        horizontal=True,
        index=None, key='feedback_1', label_visibility='collapsed')

st.divider()

col21, col22 = st.columns([0.69, 0.31])
with col21:
    rec_two = recommended_books[1]
    st.image(rec_two[2], width=100)
    st.markdown(f'<p class="title-font">{rec_two[0]}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="author-font">{rec_two[1]}</p>', unsafe_allow_html=True)
with col22:
    feedback_2 = st.radio(
        "Is this recommendation useful?",
        [":thumbsup:", ":thumbsdown:"],
        horizontal=True,
        index=None, key='feedback_2', label_visibility='collapsed')

st.divider()

col31, col32 = st.columns([0.69, 0.31])
with col31:
    rec_three = recommended_books[2]
    st.image(rec_three[2], width=100)
    st.markdown(f'<p class="title-font">{rec_three[0]}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="author-font">{rec_three[1]}</p>', unsafe_allow_html=True)
with col32:
    feedback_3 = st.radio(
        "Is this recommendation useful?",
        [":thumbsup:", ":thumbsdown:"],
        horizontal=True,
        index=None, key='feedback_3', label_visibility='collapsed')

st.divider()

col41, col42 = st.columns([0.69, 0.31])
with col41:
    rec_four = recommended_books[3]
    st.image(rec_four[2], width=100)
    st.markdown(f'<p class="title-font">{rec_four[0]}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="author-font">{rec_four[1]}</p>', unsafe_allow_html=True)
with col42:
    feedback_4 = st.radio(
        "Is this recommendation useful?",
        [":thumbsup:", ":thumbsdown:"],
        horizontal=True,
        index=None, key='feedback_4', label_visibility='collapsed')

st.divider()

col51, col52 = st.columns([0.69, 0.31])
with col51:
    rec_five = recommended_books[4]
    st.image(rec_five[2], width=100)
    st.markdown(f'<p class="title-font">{rec_five[0]}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="author-font">{rec_five[1]}</p>', unsafe_allow_html=True)
with col52:
    feedback_5 = st.radio(
        "Is this recommendation useful?",
        [":thumbsup:", ":thumbsdown:"],
        horizontal=True,
        index=None, key='feedback_5', label_visibility='collapsed')


st.text("")
st.text("")
st.write("##### Please find below your :rainbow[Wildcard] recommendation :black_joker:")
st.text("")

col61, col62 = st.columns([0.69, 0.31])
with col61:
    wildcard = wildcard_book[0]
    st.image(wildcard[2], width=100)
    st.markdown(f'<p class="title-font">{wildcard[0]}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="author-font">{wildcard[1]}</p>', unsafe_allow_html=True)
with col62:
    feedback_wc = st.radio(
        "Is this recommendation useful?",
        [":thumbsup:", ":thumbsdown:"],
        horizontal=True,
        index=None, key='feedback_wild', label_visibility='collapsed')

st.divider()

st.write("##### How was your experience using this app? :woman-shrugging:")
st.text("")
st.markdown('Please type your name (or an alias)')
user_name = st.text_input("Please type your name (or an alias)", label_visibility='collapsed',
                          placeholder='Type your name (or an alias) here ...')

st.text("")
st.markdown("Was this app easy to use? (**1** being very difficult and **5** being very easy)")
CES = st.slider("Was this app easy to use?", min_value=1, max_value=5, step=1, label_visibility='collapsed')

st.text("")
st.markdown("How likely are you to recommend this app to a friend? (**1** being not likely and **5** being very likely)")
NPS = st.slider("How likely are you to recommend this app to a friend?", min_value=1, max_value=5, step=1,
                label_visibility='collapsed')

st.text("")
col71, col72, col73 = st.columns([0.1, 0.68, 0.22])
with col71:
    back_button = st.button('Back', key='back_button')
with col73:
    submit_feedback = st.button('Submit Feedback', key='submit_feedback', type='primary')


if back_button:
    switch_page('disliked')
if submit_feedback:
    feedback_variables = [feedback_1, feedback_2, feedback_3, feedback_4, feedback_5, feedback_wc]
    if any(variable is None for variable in feedback_variables):
        st.error('Please provide feedback for all recommendations!', icon="🚨")
    elif user_name is None or user_name == '':
        st.error('Please provide a name (or an alias) above!', icon="🚨")
    else:
        if feedback_1 == ':thumbsup:':
            feedback_1 = 1
        else:
            feedback_1 = 0
        if feedback_2 == ':thumbsup:':
            feedback_2 = 1
        else:
            feedback_2 = 0
        if feedback_3 == ':thumbsup:':
            feedback_3 = 1
        else:
            feedback_3 = 0
        if feedback_4 == ':thumbsup:':
            feedback_4 = 1
        else:
            feedback_4 = 0
        if feedback_5 == ':thumbsup:':
            feedback_5 = 1
        else:
            feedback_5 = 0
        if feedback_wc == ':thumbsup:':
            feedback_wc = 1
        else:
            feedback_wc = 0
        store_feedback(user_name, feedback_1, feedback_2, feedback_3, feedback_4, feedback_5, feedback_wc, CES, NPS)
        switch_page('finish')
