import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.utils.extmath import randomized_svd
import toml
import requests
import psycopg2

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

    
class CollaborativeFiltering():
    def __init__(self, book_data=None, interactions_data=None):
        if book_data is None:
            self.book_data = self.get_book_data()
        else:
            self.book_data = book_data
        self.book_data = self.book_data.sort_values(by='book_id')
        self.book_data = self.book_data.drop_duplicates()
        self.book_data.reset_index(drop=True, inplace=True)
        
        if interactions_data is None:
            self.interactions_data = self.get_interactions_data()
        else:
            self.interactions_data = interactions_data

        self.matrix = None
        #settings
        self.k = 50
        self.c_components = 15
        self.n_iter = 5
        self.random_state = 42
        self.all_recommendations = []

    
    
    def get_book_data(self):
        query_f = """SELECT book_id
                   FROM english_books""" 
        cursor.execute(query_f)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        english_books = pd.DataFrame(rows, columns=columns)
        self.book_data = english_books
        return english_books

    
    def get_interactions_data(self):
        query_I = """SELECT *
                   FROM adjusted_ratings""" 
        cursor.execute(query_I)
        rows2 = cursor.fetchall()
        columns2 = [desc[0] for desc in cursor.description]
        interactions_data = pd.DataFrame(rows2, columns=columns2)
        self.interactions_data = interactions_data
        return english_books
        #return pd.read_csv("./data/interactions_with_adjusted_ratings.csv", engine='python', delimiter=',', encoding='latin1')


    def init_model(self):
        matrix = csr_matrix((self.interactions_data.rating.values, (self.interactions_data.user_id.values, self.interactions_data.book_id.values)))
        U, S, V = randomized_svd(matrix, 
                              n_components=self.n_components,
                              n_iter=self.n_iter,
                              random_state=self.random_state)
        self.matrix = V.T[:, :self.k]

    def cache_single_book_recommendation(self, id, like, top_n):
        #like = -1, dislike = 1
        self.all_recommendations.append(self.get_recommendation(id, top_n, like))

    def get_all_recommendations(self, liked_book_ids, disliked_book_ids, top_n):
        for liked_book_id in liked_book_ids:
            self.all_recommendations.append(self.get_recommendation(liked_book_id, top_n, -1))
        for disliked_book_id in disliked_book_ids:
            self.all_recommendations.append(self.get_recommendation(disliked_book_id, top_n, 1))
        
        return self.get_recommendations_from_cache(top_n)
    
    def get_recommendations_from_cache(self, top_n):
        filtered_recommendations = []
        for i in range(len(self.all_recommendations)):
            if len(filtered_recommendations) == top_n - 1:
                return (filtered_recommendations, self.get_wild_card(self.all_recommendations, filtered_recommendations))
            for j in range(top_n - 1):
                filtered_recommendations.append(self.all_recommendations[i][j])
        return None
    
    def get_recommendation(self, id, top_n, sort_method):
        recommendations = []
        indexes = self.top_cosine_similarity(self.matrix, id, top_n, sort_method)
        for index in indexes + 1:
            if index in self.book_data.index:
                recommendations.append(self.book_data.iloc[index].book_id)
            else:
                recommendations.append(self.book_data[self.book_data["book_id"] == index - 1].book_id.values[0])
    
    def get_wild_card(self, all_recommendations, filtered_recommendations):
        all_recommendations_flat = all_recommendations
        all_recommendations_info = []
        for id in all_recommendations_flat:
            new_book = {"id": id,
                         "rating": self.book_data[self.book_data["book_id"] == id].average_rating,
                         "rating_count": self.book_data[self.book_data["book_id"] == id].rating_count}
            all_recommendations_info.append(new_book)
        all_recommendations_info = sorted(all_recommendations_info, key=lambda x: (-x.rating, x.rating_count))
        for recommendation in all_recommendations_info:
            if recommendation.id not in filtered_recommendations:
                return recommendation.id
        return None

    def top_cosine_similarity(self, data, book_id, sort_method):
        index = book_id - 1
        book_row = data[index, :]
        magnitude = np.sqrt(np.einsum('ij, ij -> i', data, data))
        similarity = np.dot(book_row, data.T) / (magnitude[index] * magnitude)
        sort_indexes = np.argsort(sort_method * similarity)
        return sort_indexes[:self.top_n]
