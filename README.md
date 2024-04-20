## *Book Club* Recommendation System 📖

<img src="BookClub/iStock-498888964.jpg" width="400" height="300" align="right" width="200" alt="Floating Image">
### Description
The Book Club application will assist users in finding their next read by implementing a hybrid recommendation system which incorporates sentimental analysis for recommendations that tend away from the highly rated and predictable choices. Users can also look forward to a 'Wild Card' recommendation that suggests a book based on genre selection rather than personalisation which provides a greater variety in a user's bookshelf. 

This application was developed using Python and Streamlit. The data was stored and accessed using PostgreSQL. 

Future developments will include providing users with links to purchase the recommended books and scaling the application with expanding book data and user bases. 

### Installation

In order to install and set up the Book Club recommendation system, please perform the following steps:
1. The Book Club recommendation system requires certain Python packages to run. These Python packages along with their
version numbers are present in the `requirements.txt` file. Please install these Python packages into your Python environment
by using the command `pip install -r requirements.txt`.
2. In order to connect to the backend PostgreSQL database within the application, we are currently storing the database credentials
within a `secrets.toml` file. Although this file is not required in order to demo the deployed streamlit app, if there is a
need to run the developed Book Club recommendation system app on a local computer, this file is available upon request.
3. Download the source code of the Book Club recommendation system from GitHub and place it within a directory on your
local computer.

### Execution

In order to run a demo of the Book Club recommendation system, perform the following steps:

1. Open a command prompt window on your local computer (or Terminal in case of MacOS) and `cd` into the Book Club directory. 
Once inside the Book Club directory, run the command `streamlit run welcome_page.py` to open the developed Book Club
recommendation streamlit app within your default web browser.
2. Follow the instructions within the app to receive recommendations from the app. Once recommendations have been received,
provide feedback for each recommendation by clicking either 👍 or 👎 next to each recommendation.


<p align="center">
  <img src="BookClub/iStock-1030308064.jpg" width="300" height="200" alt="Centered Image">
</p>
