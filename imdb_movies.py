# Cmd execute: python imdb.py "https://www.imdb.com/india/top-rated-indian-movies" 5

from bs4 import BeautifulSoup
import requests
import sys
import json

# Constants
IMDB_URL = 'http://www.imdb.com'
TITLE_COLUMN_CLASS = "titleColumn"
RATING_COLUMN_CLASS = "ratingColumn imdbRating"
SUMMARY_TEXT_CLASS = "summary_text"
MOVIE_TITLE_WRAPPER = "title_wrapper"
SUBTEXT_CLASS = "subtext"

# Class to represent the movie object
class MovieObject(object): 
    movie_title = ""
    movie_release_year = ""
    imdb_rating = ""
    movie_summary = ""
    movie_duration = ""
    movie_genre = ""
    
    def __init__(self, title, year, rating, summary, duration, genre):
        self.movie_title = title
        self.movie_release_year = year
        self.imdb_rating = rating
        self.movie_summary = summary
        self.movie_duration = duration
        self.movie_genre = genre
        
# Getting list of movies and their respective ratings
def get_imd_movies(list_url, n):
    page = requests.get(list_url)
    soup = BeautifulSoup(page.text, 'html.parser')
    movies = soup.find_all("td", class_= TITLE_COLUMN_CLASS)
    ratings = soup.find_all("td", class_= RATING_COLUMN_CLASS)
    return movies[:n], ratings[:n]

# Movie details that can be obtained only after navigating to the movie's page
def movie_info_movie_page(url):
    movie_page = requests.get(url)
    soup = BeautifulSoup(movie_page.text, 'html.parser')
    summary = soup.find("div", class_= SUMMARY_TEXT_CLASS).contents[0].strip()
    duration = soup.find("div", class_= MOVIE_TITLE_WRAPPER).find("div", class_= SUBTEXT_CLASS).find("time").contents[0].strip()
    genre = soup.find("div", class_= MOVIE_TITLE_WRAPPER).find("div", class_= SUBTEXT_CLASS).find("a").contents[0].strip()
    return summary, duration, genre

# Movie details that can be scraped directly from the list page
def movie_info_list_page(movie):
    movie_title = movie.a.contents[0]
    movie_year = movie.span.contents[0]
    movie_url = IMDB_URL + movie.a['href']
    return movie_title, movie_year, movie_url

def get_movie_rating(rating):
    movie_rating = rating.strong.contents[0]
    return movie_rating
    
def get_movie_data_by_url(list_url, n):
    movie_list = []
    movies, ratings = get_imd_movies(list_url, n)
    for idx in range(0, n):
        movie = movies[idx]
        rating = ratings[idx]
        movie_title, movie_year, movie_url = movie_info_list_page(movie)
        movie_rating = get_movie_rating(rating)
        movie_summary, movie_duration, movie_genre = movie_info_movie_page(movie_url)
        movie_object = MovieObject(movie_title, movie_year[1: -1], movie_rating, movie_summary, movie_duration, movie_genre)
        movie_list.append(movie_object)
        print(idx + 1, " Fetched -> ", movie_title)
    return movie_list

# Converting list of MovieObject to json list representation
def get_json(movie_list):
    return json.dumps([movie.__dict__ for movie in movie_list]) 
        
if __name__ == '__main__':
    imdb_movies_object_list = get_movie_data_by_url(sys.argv[1], int(sys.argv[2]))
    imdb_movies_json_list = get_json(imdb_movies_object_list)
    print("\n\n", "JSON: ", "\n\n")
    print(imdb_movies_json_list)