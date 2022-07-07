import requests
import tmdbsimple as tmdb
from app.models import *
from app.decorators import timed
from sqlalchemy.inspection import inspect
from typing import Union, List, Tuple, Set

DatabaseType = Union[Director, Country, Year, Actor, Actress, Genre]


@timed
def extract_films_not_in_db(film_objects):

    db_ids = find_all_ids_in_db()

    films_not_in_db = []
    for film in film_objects:
        if int(film['letterboxd_id']) not in db_ids:
            films_not_in_db.append(film)

    return films_not_in_db


def find_all_ids_in_db() -> Set[int]:
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
        print(film['film_title'], film['tmdb_id'],
              '{}/{}'.format(i + 1, nr_films))
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

    ''' This part adds year to the database '''
    release_date = tmdb_film_info['release_date']
    release_year = release_date.partition('-')[0]
    if year_is_in_db(release_year):
        Year.query.get(release_year).films.append(db_film)
    else:
        db_year = Year(name=release_year)
        db_year.films.append(db_film)
        db.session.add(db_year)

    ''' This part adds actor to the database '''
    cast = tmdb_film.credits()['cast']
    nr_actors = max(len(cast)//4, 15)
    actors = [credit for i, credit in zip(
        range(nr_actors), cast) if credit['gender'] == 2]
    actresses = [credit for i, credit in zip(
        range(nr_actors), cast) if credit['gender'] == 1]

    for actor in actors:
        if actor_is_in_db(actor):
            Actor.query.get(actor['id']).films.append(db_film)
        else:
            db_actor = Actor(id=actor['id'], name=actor['name'])
            db_actor.films.append(db_film)
            db.session.add(db_actor)

    for actress in actresses:
        if actress_is_in_db(actress):
            Actress.query.get(actress['id']).films.append(db_film)
        else:
            db_actress = Actress(id=actress['id'], name=actress['name'])
            db_actress.films.append(db_film)
            db.session.add(db_actress)

    ''' This part adds genre to the database '''
    genres = tmdb_film_info['genres']
    for genre in genres:
        if genre_is_in_db(genre):
            Genre.query.get(genre['name']).films.append(db_film)
        else:
            db_genre = Genre(name=genre['name'])
            db_genre.films.append(db_film)
            db.session.add(db_genre)
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


def director_is_in_db(director: dict) -> bool:
    return Director.query.get(int(director['id'])) is not None


def country_is_in_db(country: dict) -> bool:
    return Country.query.get(country['name']) is not None


def year_is_in_db(year: str) -> bool:
    return Year.query.get(year) is not None


def actor_is_in_db(actor: dict) -> bool:
    return Actor.query.get(actor['id']) is not None


def actress_is_in_db(actress: dict) -> bool:
    return Actress.query.get(actress['id']) is not None


def genre_is_in_db(genre: dict) -> bool:
    return Genre.query.get(genre['name']) is not None


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
    Query the category of each film in the database.

    Returned dictionary constructed as:
    key - letterboxd_id(int), value - category.

    Returns
    -------
    dict
        Dictionary of {int: models.*}.
    """
    db_films = Film.query.all()
    db_category_of_db_film = {film.letterboxd_id: getattr(film, category_type.lower()) for film in db_films}
    return db_category_of_db_film


def user_in_db(username):
    return User.query.get(username) is not None


def query_user_attr(username: str, attr_type: str) -> List[Tuple]:
    user = User.query.get(username)
    return getattr(user, attr_type.lower())


def add_user_to_db(username, logged_films_compact, pages, avatar_url):
    user = User(username=username,
                film=logged_films_compact,
                pages=pages,
                avatar_url=avatar_url,
                director=None)
    db.session.add(user)
    db.session.commit()
    print('User {} added to database'.format(username))


def update_db_user(username, logged_films_compact, pages, avatar_url):
    user = User.query.get(username)
    user.films= logged_films_compact
    user.pages = pages
    user.avatar_url = avatar_url
    db.session.commit()


def update_db_user_category(username: str, category: List[Tuple], category_type: str) -> None:
    user = User.query.get(username)
    setattr(user, category_type.lower(), category)
    db.session.commit()


def get_primary_key(category: DatabaseType) -> Union[int, str]:
    return inspect(category).identity[0]


def query_user_films_from_year(username: str, year: str) -> List[Tuple[str, int, int]]:
    u = User.query.get(username)
    y = Year.query.get(year)

    user_film_ids = {id for (id, _) in u.film}
    year_film_ids = {film.letterboxd_id for film in y.films}

    user_film_ids_this_year = set.intersection(user_film_ids, year_film_ids)
    user_films_this_year = [(Film.query.get(film[0]).title, film[0], film[1])
                            for film in u.film if film[0] in user_film_ids_this_year]
    return user_films_this_year
