from app import db
from app.models import Film, Director, Tv, Miscellaneous
from app.scraping import get_user_ratings
from app.database import scrape_and_add_tmdb_info_to
import asyncio


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

def get_director_in_db_with_name(name):
    all_directors_with_name = []
    for director in Director.query.all():
        if director.name.lower() == name.lower():
            all_directors_with_name.append(director)
    if len(all_directors_with_name) == 0:
        print("No such director.")
    elif len(all_directors_with_name) == 1:
        return all_directors_with_name[0]
    else:
        return all_directors_with_name

def test_tmdb_info_adding():

    async def inner():
        film_objects = await get_user_ratings('kattihatt2', 1)
        print(film_objects[0])
        await scrape_and_add_tmdb_info_to([film_objects[0]])
        print(film_objects[0])

    asyncio.set_event_loop(asyncio.SelectorEventLoop())
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(inner())
    loop.run_until_complete(future)
