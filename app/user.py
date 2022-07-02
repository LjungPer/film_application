from audioop import avg
from app.decorators import timed
from app.database import query_directors_of_all_db_films, query_user_films, update_db_user_directors
from app.models import User
from typing import Tuple, List
from app.categories import Director


def get_top_directors_biased(username: str, nr_items: int = 10) -> List[list]:
    """
    Return list of top directors based on biased rating.

    Each director in list is represented by a list of attributes.
    Attributes consist of name(str), avg_rating(float),  bias_rating(float) and nr_films(int).

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
        nr_films = director[4]
        top_directors.append([name, avg_rating, bias_rating, nr_films])

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
    db_director_of_db_film = query_directors_of_all_db_films()
    user_films = query_user_films(username)
    user_directors = {}
    for film in user_films:
        index_of_film = film[0]
        if index_of_film in db_director_of_db_film:
            db_directors = db_director_of_db_film[index_of_film]
            for db_director in db_directors:
                if db_director.id in user_directors:
                    user_directors[db_director.id].append_film(film)
                else:
                    user_directors[db_director.id] = Director(
                        name=db_director.name)
                    user_directors[db_director.id].append_film(film)

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
    nr_films = director.number_of_films

    return key, name, avg_rating, bias_rating, nr_films
