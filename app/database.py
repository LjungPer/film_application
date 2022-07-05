from attr import attr
import requests
import tmdbsimple as tmdb
from app.models import *
from app.decorators import timed
from sqlalchemy.inspection import inspect
from typing import Union, List, Tuple

@timed
def extract_films_not_in_db(film_objects):

    db_ids = find_all_ids_in_db()

    films_not_in_db = []
    for film in film_objects:
        if int(film['letterboxd_id']) not in db_ids:
            films_not_in_db.append(film)

    return films_not_in_db


def find_all_ids_in_db():
    film_ids = db.session.query(Film.letterboxd_id).all()
    tv_ids = db.session.query(Tv.letterboxd_id).all()
    misc_ids = db.session.query(Miscellaneous.letterboxd_id).all()
    all_ids = set.union({id for (id,) in film_ids}, {
                        id for (id,) in tv_ids}, {id for (id,) in misc_ids})

    return all_ids


@timed
def add_films_to_db(films_not_in_db):
    nr_films = len(films_not_in_db)
    for i, film in zip(range(nr_films), films_not_in_db):
        print(film['film_title'], film['tmdb_id'], '{}/{}'.format(i + 1, nr_films))
        if film['movie']:
            add_movie_and_director_to_db(film)
        if film['tv']:
            add_tv_to_db(film)


def add_movie_and_director_to_db(film):
    ''' Mayhaps this can be better written, but should check how the database objects are related and used. '''

    if missing_from_tmdb(film):
        add_misc_to_db(film)
        print('Added {title} to Miscallaneous'.format(
            title=film['film_title']))
        return

    ''' This part adds the film to the database. '''
    tmdb_film = tmdb.Movies(film['tmdb_id'])
    tmdb_film_info = tmdb_film.info()
    db_film = Film(tmdb_id=int(film['tmdb_id']), title=tmdb_film_info['title'],
                   letterboxd_id=int(film['letterboxd_id']))
    db.session.add(db_film)

    ''' This part adds the director to the database. '''
    directors_of_film = find_directors_of_movie(tmdb_film)
    for director in directors_of_film:
        if director_is_in_db(director):
            Director.query.get(int(director['id'])).films.append(db_film)
        else:
            db_director = Director(
                id=director['id'], name=director['name'])
            db_director.films.append(db_film)
            db.session.add(db_director)

    ''' This part adds country to the database '''
    production_countries = tmdb_film_info['production_countries']
    for country in production_countries:
        if country_is_in_db(country):
            Country.query.get(country['name']).films.append(db_film)
        else:
            db_country = Country(name=country['name'])
            db_country.films.append(db_film)
            db.session.add(db_country)
    db.session.commit()

def find_directors_of_movie(tmdb_film):
    directors = [credit for credit in tmdb_film.credits()['crew']
                 if credit["job"] == "Director"]
    return directors


def missing_from_tmdb(film):
    tmdb_film = tmdb.Movies(film['tmdb_id'])
    try:
        tmdb_film.info()
    except requests.HTTPError as exception:
        print(exception)
        return True
    return False


def add_misc_to_db(film):
    misc = Miscellaneous(letterboxd_id=int(
        film['letterboxd_id']), title=film['film_title'])
    db.session.add(misc)
    db.session.commit()


def director_is_in_db(director):
    return Director.query.get(int(director['id'])) is not None

def country_is_in_db(country):
    return Country.query.get(country['name']) is not None


def add_tv_to_db(film):
    print(film['film_title'], film['tmdb_id'])
    tmdb_film = tmdb.TV(film['tmdb_id'])
    tmbd_film_info = tmdb_film.info()
    db_tv = Tv(tmdb_id=int(film['tmdb_id']), title=tmbd_film_info['name'], letterboxd_id=int(
        film['letterboxd_id']))
    db.session.add(db_tv)
    db.session.commit()



@timed
def query_category_of_all_db_films(category_type: str) -> dict:
    """
    Query the director of each film in the database.

    Returned dictionary constructed as:
    key - letterboxd_id(int), value - director(models.Director).

    Returns
    -------
    dict
        Dictionary of {int: models.Director}.
    """
    db_films = Film.query.all()
    if category_type == 'Director':
        db_category_of_db_film = {
            film.letterboxd_id: film.director for film in db_films}
    elif category_type == 'Country':
        db_category_of_db_film = {
            film.letterboxd_id: film.country for film in db_films}
    else:
        return {}
    return db_category_of_db_film

@timed
def query_directors_of_all_db_films() -> dict:
    """
    Query the director of each film in the database.

    Returned dictionary constructed as:
    key - letterboxd_id(int), value - director(models.Director).

    Returns
    -------
    dict
        Dictionary of {int: models.Director}.
    """
    db_films = Film.query.all()
    db_director_of_db_film = {
        film.letterboxd_id: film.director for film in db_films}
    return db_director_of_db_film


@timed
def query_countries_of_all_db_films() -> dict:
    """
    Query the director of each film in the database.

    Returned dictionary constructed as:
    key - letterboxd_id(int), value - director(models.Director).

    Returns
    -------
    dict
        Dictionary of {int: models.Director}.
    """
    db_films = Film.query.all()
    db_countries_of_db_film = {
        film.letterboxd_id: film.country for film in db_films}
    return db_countries_of_db_film


def user_in_db(username):
    return User.query.get(username) is not None


def query_user_attr(username: str, attr_type: str) -> List[Tuple]:
    user = User.query.get(username)
    if attr_type == 'Film':
        return user.logged_films
    elif attr_type == 'Director':
        return user.directors
    elif attr_type == 'Country':
        return user.countries
    else:
        raise TypeError('No such attribute') 


def add_user_to_db(username, logged_films_compact, num_pages, avatar_url):
    user = User(username=username,
                logged_films=logged_films_compact,
                num_pages=num_pages,
                avatar_url=avatar_url,
                directors=None)
    db.session.add(user)
    db.session.commit()
    print('User {} added to database'.format(username))


def update_db_user(username, logged_films_compact, num_pages, avatar_url):
    user = User.query.get(username)
    user.logged_films = logged_films_compact
    user.num_pages = num_pages
    user.avatar_url = avatar_url
    db.session.commit()

def update_db_user_category(username: str, category: List[Tuple], category_type: str) -> None:
    user = User.query.get(username)
    if category_type == 'Director':
        user.directors = category
    if category_type == 'Country':
        user.categories = category
    db.session.commit()

def get_primary_key(category: Union[Director, Country]) -> Union[int, str]:
    return inspect(category).identity[0]