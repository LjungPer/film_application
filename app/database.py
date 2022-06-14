import requests
import tmdbsimple as tmdb
from app.models import *
from app.decorators import timed


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
    all_ids = set.union({id for (id,) in film_ids}, {id for (id,) in tv_ids}, {id for (id,) in misc_ids})

    return all_ids


@timed
def add_films_to_db(films_not_in_db):
    for film in films_not_in_db:
        if film['movie']:
            add_movie_and_director_to_db(film)
        if film['tv']:
            add_tv_to_db(film)


def add_movie_and_director_to_db(film):
    ''' Mayhaps this can be better written, but should check how the database objects are related and used. '''

    print(film['film_title'], film['tmdb_id'])
    if missing_from_tmdb(film):
        add_misc_to_db(film)
        print('Added {title} to Miscallaneous'.format(title=film['film_title']))
        return

    ''' This parts add the film to the database. '''
    tmdb_film = tmdb.Movies(film['tmdb_id'])
    tmdb_film.info()
    db_film = Film(tmdb_id=int(film['tmdb_id']), title=tmdb_film.title,
                   letterboxd_id=int(film['letterboxd_id']))
    db.session.add(db_film)

    ''' This parts add the director to the database. '''
    ''' Make this as a function named find_directors_of_movie(tmdb_film). '''
    directors = [credit for credit in tmdb_film.credits()['crew'] if credit["job"] == "Director"]
    for director in directors:
        if director_is_in_db(director):
            Director.query.get(int(director['id'])).films.append(db_film)
        else:
            db_director = Director(director_id=director['id'], name=director['name'])
            db_director.films.append(db_film)
            db.session.add(db_director)
    db.session.commit()
    ''' Check if db should be closed somehow to prevent issue with db not accepting more session or something'''


def missing_from_tmdb(film):
    tmdb_film = tmdb.Movies(film['tmdb_id'])
    try:
        tmdb_film.info()
    except requests.HTTPError as exception:
        print(exception)
        return True
    return False


def add_misc_to_db(film):
    misc = Miscellaneous(letterboxd_id=int(film['letterboxd_id']), title=film['film_title'])
    db.session.add(misc)
    db.session.commit()


def director_is_in_db(director):
    ''' Try do write this shorter, e.g. Director.query.get(int(director['id'])) is not None '''
    return db.session.query(Director.director_id).filter_by(director_id=int(director['id'])).first() is not None


def add_tv_to_db(film):
    print(film['film_title'], film['tmdb_id'])
    tmdb_film = tmdb.TV(film['tmdb_id'])
    tmdb_film.info()
    db_tv = Tv(tmdb_id=int(film['tmdb_id']), title=tmdb_film.name, letterboxd_id=int(film['letterboxd_id']))
    db.session.add(db_tv)
    db.session.commit()

@timed
def get_directors_of_films():
    db_films = Film.query.all()
    db_director_of_db_film = {film.letterboxd_id: film.director for film in db_films}
    return db_director_of_db_film


def user_is_not_in_db(username):
    return User.query.get(username) is None


def add_user_to_db(username, logged_films, num_pages, avatar_url):
    user = User(username=username, logged_films=logged_films, num_pages=num_pages, avatar_url=avatar_url)
    db.session.add(user)
    db.session.commit()
    print('User {} added to database'.format(username))


def update_db_user(username, logged_films, num_pages, avatar_url):
    user = User.query.get(username)
    user.logged_films = logged_films
    user.num_pages = num_pages
    user.avatar_url = avatar_url
    db.session.commit()
