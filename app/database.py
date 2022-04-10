from bs4 import BeautifulSoup, SoupStrainer
import requests
import asyncio
from aiohttp import ClientSession
import re
import tmdbsimple as tmdb
from app.models import *
import time


''' How to name this file? '''

async def update_database_with_new_films(user_films):
    films_not_in_db = extract_films_not_in_db(user_films)
    await scrape_and_add_tmdb_info_to(films_not_in_db)
    add_films_to_db(films_not_in_db)


def extract_films_not_in_db(film_objects):
    start = time.time()
    db_ids = find_all_indices_in_db()

    films_not_in_db = []
    for film in film_objects:
        if int(film['letterboxd_id']) in db_ids:
            continue
        else:
            films_not_in_db.append(film)
    end = time.time()
    print('Time to loop through film_objects is {time}'.format(time=end - start))

    return films_not_in_db


def find_all_indices_in_db():
    film_ids = db.session.query(Film.letterboxd_id).all()
    tv_ids = db.session.query(Tv.letterboxd_id).all()
    misc_ids = db.session.query(Miscellaneous.letterboxd_id).all()
    all_ids = set.union({id for (id,) in film_ids}, {id for (id,) in tv_ids}, {id for (id,) in misc_ids})

    return all_ids


async def scrape_and_add_tmdb_info_to(films):
    start = time.time()
    scrape_responses = await scrape_letterboxd_urls_of(films)
    add_scraped_info_to(films, scrape_responses)
    end = time.time()
    print('Time to deal with scraping is {time}'.format(time=end - start))


async def scrape_letterboxd_urls_of(films):
    async with ClientSession() as session:
        tasks = []
        for film in films:
            task = asyncio.ensure_future(fetch(film['url'], session))
            tasks.append(task)

        scrape_responses = await asyncio.gather(*tasks)
    return scrape_responses


def add_scraped_info_to(films, scrape_responses):
    relevant = SoupStrainer('a', attrs={"class": "micro-button track-event", "data-track-action": "TMDb"})
    index = 0
    for response in scrape_responses:
        soup = BeautifulSoup(response, "lxml", parse_only=relevant)
        tmp = soup.find('a', attrs={"class": "micro-button track-event", "data-track-action": "TMDb"})['href']

        if re.search('movie/(.*)/', tmp) is not None:
            tmdb_id = re.search('movie/(.*)/', tmp).group(1)
            films[index]['tmdb_id'] = tmdb_id
            films[index]['movie'] = True

        if re.search('tv/(.*)/', tmp) is not None:
            tmdb_id = re.search('tv/(.*)/', tmp).group(1)
            films[index]['tmdb_id'] = tmdb_id
            films[index]['tv'] = True
        index += 1



async def fetch(url, session):
    async with session.get(url) as response:
        return await response.read()


def add_films_to_db(films_not_in_db):
    start = time.time()
    for film in films_not_in_db:
        if film['movie']:
            add_movie_and_director_to_db(film)
        if film['tv']:
            add_tv_to_db(film)

    end = time.time()
    print('Time for last loop in update database is {time}'.format(time=end - start))


def add_movie_and_director_to_db(film):
    ''' This function does several things, and should probably be split into several. However, I don't see how to split
        the adding of db_film and adding of db_director, since the db_director also requires db_film. You could query it
        from the database inside a "add_director()"-function, but that time consuming. You could pass db_film as an
        argument, but then you also have to return it from a "add_movie()"-function, which won't look so clean either.'''

    ''' Also, the function name isn't particularly pretty. Any ideas? '''

    print(film['film_title'], film['tmdb_id'])
    if is_misc(film):
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
    directors = [credit for credit in tmdb_film.credits()['crew'] if credit["job"] == "Director"]
    for director in directors:
        if director_is_in_db(director):
            Director.query.get(int(director['id'])).films.append(db_film)
        else:
            db_director = Director(director_id=director['id'], name=director['name'])
            db_director.films.append(db_film)
            db.session.add(db_director)
    db.session.commit()


def is_misc(film):
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
    ''' Should this be written on several lines to clarify how it checks if director is in db?'''
    return db.session.query(Director.director_id).filter_by(director_id=int(director['id'])).first() is not None

def add_tv_to_db(film):
    print(film['film_title'], film['tmdb_id'])
    tmdb_film = tmdb.TV(film['tmdb_id'])
    tmdb_film.info()
    db_tv = Tv(tmdb_id=int(film['tmdb_id']), title=tmdb_film.name, letterboxd_id=int(film['letterboxd_id']))
    db.session.add(db_tv)
    db.session.commit()
