todo:
collab filtering:
filter by filtered dataset on rating_data.csv
intergrate into hybrid model
split get_recommendations function into building all_recommendations list + filtering for final recommendations
maybe: split input data by genre, create different matrices + load them accordingly (probably not necessary for 32GB machine)

content based filtering:
build content based filtering class
provide function for usage in hybrid filtering
integrate into hybrid model (create instance of the class, get recommendations)

sentiment analysis:
filter by filtered dataset
original approach + genre approach (poetry)
original approach -> content based filtering (book_id)
genre approach -> collab filtering + content based filtering (user_id + book_id)
"merge" resulting data with the dataset from vebash and raven (content based) + interactions dataset (colab filtering)

hybrid filtering:
2 recommendations for each + 1 wild card

front end:
filter by filtered dataset
run get_recommendation per selection

dataset:
provide final dataset already filtered by language providing book_id, genre etc. - "filtered dataset"

============

misc:
deployment - do deployment on aws, get feedback + analyse/summarize results
doc for content based filtering
doc for collaborative filtering
doc for sentiment analysis
doc for hybrid approach
doc for front end / UX
doc for experimentation: what have we done that has not worked?
doc for user experiment + results
poster
clean up code base + technical doc