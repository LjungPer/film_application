import asyncio
from app.manager import get_user_films
from app.decorators import timed
from app.database import get_directors_of_films, query_user_films, update_db_user_directors
from app.models import User, Director
from app import db



def collect_directors(username):
    db_director_of_db_film = get_directors_of_films()
    user_films = query_user_films(username)
    user_directors = {}
    for film in user_films:
        index_of_film = int(film[0])
        if index_of_film in db_director_of_db_film:
            directors = db_director_of_db_film[index_of_film]
            for director in directors:
                if director.director_id in user_directors:
                    user_directors[director.director_id].add_film(film)
                else:
                    user_directors[director.director_id] = Directortmp(name=director.name)
                    user_directors[director.director_id].add_film(film)

    return user_directors


def compute_scores(directors):

    directors_with_scores = []
    for key in directors:
        directors[key].compute_average_rating()
        directors[key].compute_biased_rating()
        tup = (key, directors[key].name, directors[key].get_average_rating(), directors[key].get_biased_rating())
        directors_with_scores.append(tup)

    return directors_with_scores


def get_directors_sorted_by_biased(username):
    user = User.query.get(username)
    if user.directors is None:
        user_directors = collect_directors(username)
        directors_with_scores = compute_scores(user_directors)
        update_db_user_directors(username, directors_with_scores)

    sorted_directors = sorted(user.directors, key=lambda x: x[3], reverse=True)
    return sorted_directors


def get_top_directors_biased(username, number_of_directors=10):
    sorted_directors = get_directors_sorted_by_biased(username)
    return [[el[1], round(el[3], 2)] for (i, el) in zip(range(number_of_directors), sorted_directors)]

    

class Directortmp:
    def __init__(self, name):
        self.name = name
        self.films = []
        self.average_rating = None
        self.biased_rating = None

    def get_name(self):
        return self.name

    def get_average_rating(self):
        return self.average_rating

    def get_biased_rating(self):
        return self.biased_rating

    def add_film(self, Film):
        self.films.append(Film)

    def print_films(self):
        for film in self.films:
            print('%s  %s' %(film.title, film.rating))

    def compute_average_rating(self):
        tot_rating = 0
        no_rated_films = 0
        for film in self.films:
            rating = film[1]
            if rating is not None:
                tot_rating += rating
                no_rated_films += 1
        if no_rated_films > 0:
            self.average_rating = tot_rating / no_rated_films
        else:
            self.average_rating = 0

    def compute_biased_rating(self):
        self.compute_average_rating()
        no_films = len(self.films)
        biased_factor = 1 - 0.8 / no_films

        self.biased_rating = self.average_rating * biased_factor