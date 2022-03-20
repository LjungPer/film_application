from bs4 import BeautifulSoup, SoupStrainer
import requests
import asyncio
from aiohttp import ClientSession
import re
import tmdbsimple as tmdb
from app.models import *
import time


async def fetch(url, session):
    async with session.get(url) as response:
        return await response.read()


async def update_database(film_objects):
    '''
    Currently things like Dekalog are not added to db, yet takes minor time due to added in films_to_be_added
    '''

    # Check what films that are not in the database
    start = time.time()
    film_ids = db.session.query(Film.letterboxd_id).all()
    tv_ids = db.session.query(Tv.letterboxd_id).all()
    misc_ids = db.session.query(Miscellaneous.letterboxd_id).all()
    ids = set.union({id for (id,) in film_ids}, {id for (id,) in tv_ids}, {id for (id,) in misc_ids})
    films_to_be_added = []
    for film in film_objects:
        if int(film['letterboxd_id']) in ids:
            continue
        else:
            films_to_be_added.append(film)
    end = time.time()
    print('Time to loop through film_objects is {time}'.format(time=end-start))

    start = time.time()
    # Scrape the films
    async with ClientSession() as session:
        tasks = []

        for film in films_to_be_added:
            task = asyncio.ensure_future(fetch(film['url'], session))
            tasks.append(task)

        scrape_responses = await asyncio.gather(*tasks)

    relevant = SoupStrainer('a', attrs={"class": "micro-button track-event", "data-track-action": "TMDb"})
    count = 0
    for response in scrape_responses:

        soup = BeautifulSoup(response, "lxml", parse_only=relevant)
        tmp = soup.find('a', attrs={"class": "micro-button track-event", "data-track-action": "TMDb"})['href']

        if re.search('movie/(.*)/', tmp) is not None:
            tmdb_id = re.search('movie/(.*)/', tmp).group(1)
            films_to_be_added[count]['tmdb_id'] = tmdb_id
            films_to_be_added[count]['movie'] = True

        if re.search('tv/(.*)/', tmp) is not None:
            tmdb_id = re.search('tv/(.*)/', tmp).group(1)
            films_to_be_added[count]['tmdb_id'] = tmdb_id
            films_to_be_added[count]['tv'] = True

        count += 1
    end = time.time()
    print('Time to deal with scraping is {time}'.format(time=end-start))

    start = time.time()
    for film in films_to_be_added:
        if film['movie']:
            print(film['film_title'], film['tmdb_id'])
            tmdb_film = tmdb.Movies(film['tmdb_id'])

            try:
                tmdb_film.info()
            except requests.HTTPError as exception:
                print(exception)
                print('Added {title} to Miscallaneous'.format(title=film['film_title']))
                misc = Miscellaneous(letterboxd_id=int(film['letterboxd_id']), title=film['film_title'])
                db.session.add(misc)
                db.session.commit()
                continue


            tmpfilm = Film(tmdb_id=int(film['tmdb_id']), title=tmdb_film.title,
                           letterboxd_id=int(film['letterboxd_id']))
            db.session.add(tmpfilm)

            directors = [credit for credit in tmdb_film.credits()['crew'] if credit["job"] == "Director"]
            for director in directors:
                if db.session.query(Director.director_id).filter_by(director_id=int(director['id'])).first() is None:
                    tmpdirector = Director(director_id=director['id'], name=director['name'])
                    tmpdirector.films.append(tmpfilm)
                    db.session.add(tmpdirector)
                else:
                    Director.query.get(int(director['id'])).films.append(tmpfilm)
            db.session.commit()

        if film['tv']:
            print(film['film_title'], film['tmdb_id'])
            tmdb_film = tmdb.TV(film['tmdb_id'])
            tmdb_film.info()
            tmptv = Tv(tmdb_id=int(film['tmdb_id']), title=tmdb_film.name,
                           letterboxd_id=int(film['letterboxd_id']))
            db.session.add(tmptv)
            db.session.commit()
    end = time.time()
    print('Time for last loop in update database is {time}'.format(time=end-start))

