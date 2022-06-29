from app.decorators import timed
from app.database import get_directors_of_films, query_user_films, update_db_user_directors
from app.models import User
from typing import Type, Tuple, List


class Director:
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

    def get_number_of_films(self):
        return len(self.films)

    def add_film(self, Film):
        self.films.append(Film)

    def print_films(self):
        for film in self.films:
            print('%s  %s' % (film.title, film.rating))

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


def get_top_directors_biased(username: str, number_of_directors: int = 10) -> List[list]:
    sorted_directors = get_directors_sorted_by_biased(username)
    top_directors = []
    for (i, director) in zip(range(number_of_directors), sorted_directors):
        name = director[1]
        avg_rating = round(director[2], 2)
        bias_rating = round(director[3], 2)
        top_directors.append([name, avg_rating, bias_rating])

    return top_directors


def get_directors_sorted_by_biased(username: str) -> List[Tuple]:
    user = User.query.get(username)
    if user.directors is None:
        update_user_director_statistics(username)

    sorted_directors = sorted(user.directors, key=lambda x: x[3], reverse=True)
    return sorted_directors


def update_user_statistics(username: str) -> None:
    ''' Currently only does director, but can add additional statistics here.'''
    update_user_director_statistics(username)


def update_user_director_statistics(username: str) -> None:

    user_directors = collect_directors(username)
    directors_with_attributes = add_attributres_to_directors(user_directors)
    update_db_user_directors(username, directors_with_attributes)


def collect_directors(username: str) -> dict:
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
                    user_directors[director.director_id] = Director(
                        name=director.name)
                    user_directors[director.director_id].add_film(film)

    return user_directors


def add_attributres_to_directors(directors: dict) -> List[Tuple]:

    directors_with_attributes = []
    for key in directors:
        director = directors[key]
        compute_scores(director)

        attributes = get_director_attributes(key, director)
        directors_with_attributes.append(attributes)

    return directors_with_attributes


def compute_scores(director: Type[Director]) -> None:
    director.compute_average_rating()
    director.compute_biased_rating()


def get_director_attributes(key: int, director: Type[Director]) -> Tuple[int, str, float, float, int]:

    name = director.name
    avg_rating = director.get_average_rating()
    bias_rating = director.get_biased_rating()
    no_films = director.get_number_of_films()

    return key, name, avg_rating, bias_rating, no_films
