from audioop import avg
from app.decorators import timed
from app.database import get_directors_of_films, query_user_films, update_db_user_directors
from app.models import User
from typing import Type, Tuple, List


class Director:
    def __init__(self, name: str) -> None:
        self._name = name
        self._average_rating = None
        self._biased_rating = None
        self.films = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def average_rating(self) -> float:

        if self._average_rating is None:
            self._average_rating = round(self.compute_average_rating(), 2)
        return self._average_rating

    @property
    def biased_rating(self) -> float:
        if self._biased_rating is None:
            self._biased_rating = round(self.compute_biased_rating(), 2)
        return self._biased_rating

    @property
    def number_of_films(self) -> int:
        return len(self.films)

    def add_film(self, film):
        self.films.append(film)

    def compute_average_rating(self) -> float:
        tot_rating = 0
        nr_rated_films = 0
        for film in self.films:
            rating = film[1]
            if rating is not None:
                tot_rating += rating
                nr_rated_films += 1
        if nr_rated_films > 0:
            return tot_rating / nr_rated_films
        else:
            return 0
        

    def compute_biased_rating(self) -> float:
        nr_films = len(self.films)
        biased_factor = 1 - 0.8 / nr_films

        return self.average_rating * biased_factor


def get_top_directors_biased(username: str, nr_items: int = 10) -> List[list]:
    """
    Return list of top directors based on biased rating.

    Each director in list is represented by a list of attributes.
    Attributes consist of name(str), avg_rating(float) and bias_rating(float).

    Parameters
    ----------
    username : str

    no_items : int, optional
        Number of directors to be returned, by default 10.

    Returns
    -------
    List[list]
        List of top directors based on biased rating.
    """
    sorted_directors = get_directors_sorted_by_biased(username)
    top_directors = []
    for i, director in zip(range(nr_items), sorted_directors):
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
            db_directors = db_director_of_db_film[index_of_film]
            for db_director in db_directors:
                if db_director.id in user_directors:
                    user_directors[db_director.id].add_film(film)
                else:
                    user_directors[db_director.id] = Director(
                        name=db_director.name)
                    user_directors[db_director.id].add_film(film)

    return user_directors


def add_attributres_to_directors(directors: dict) -> List[Tuple]:

    directors_with_attributes = []
    for key in directors:
        director = directors[key]

        attributes = get_director_attributes(key, director)
        directors_with_attributes.append(attributes)

    return directors_with_attributes


def get_director_attributes(key: int, director: Director) -> Tuple[int, str, float, float, int]:

    name = director.name
    avg_rating = director.average_rating
    bias_rating = director.biased_rating
    no_films = director.number_of_films

    return key, name, avg_rating, bias_rating, no_films

