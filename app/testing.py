from app import db
from app.models import Film, Director, Tv, Miscellaneous


def get_database_film_from_title(title):
    letterboxd_ids = get_letterboxd_id_of_film(title)
    if len(letterboxd_ids) == 0:
        print('No such film in database.')
    elif len(letterboxd_ids) == 1:
        return Film.query.get(letterboxd_ids[0])
    else:
        print('%d films by that name returned.' % len(letterboxd_ids))
        return [Film.query.get(id) for id in letterboxd_ids]


def get_letterboxd_id_of_film(title):
    films_with_title = get_films_in_database_with_title(title)
    return [film.letterboxd_id for film in films_with_title]


def get_films_in_database_with_title(title):
    all_films = Film.query.all()
    films_with_title = [film for film in all_films if film.title.lower() == title.lower()]
    return films_with_title
