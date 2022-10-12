from app.scraping import get_film_entries_from_scraped_pages, scrape_list
from app.database import add_list_to_db, list_is_in_db, query_user, update_db_list, query_list, update_db_with_new_films
from app.manager import convert_films_to_ids, sort_dictionary
from typing import Tuple
import asyncio

#lb_lists = {'1001': 'https://letterboxd.com/gubarenko/list/1001-movies-you-must-see-before-you-die-2021/',
#            'letterboxd_250': 'https://letterboxd.com/dave/list/official-top-250-narrative-feature-films/',
#            'imdb_250': 'https://letterboxd.com/dave/list/imdb-top-250/',
#            'best_picture': 'https://letterboxd.com/djamesc/list/best-picture-winners-1/'
#            }
lb_lists = {'imdb_250': 'https://letterboxd.com/dave/list/imdb-top-250/'}

def list_films_seen_by_user(username: str, list_name: str) -> Tuple[float, int, int]:
    lb_list = query_list(list_name)
    list_films = lb_list.films
    user = query_user(username)
    user_films = set([id for (id,_) in user.film])
    nr_films_seen = len(set.intersection(list_films, user_films))
    percentage_seen = round(100 * nr_films_seen / len(list_films), 1)
    return percentage_seen, len(list_films), nr_films_seen

def films_sorted_by_list_points():
    d = {}
    for key in lb_lists:
        lb_list = query_list(key)
        for id in lb_list.films:
            if id in d:
                d[id] += 1
            else:
                d[id] = 1
    d = sort_dictionary(d)
    top_films = []
    for key in d:
        top_films.append((key, d[key]))
    return top_films

    
def update_all_lists():
    for key in lb_lists:
        update_list(key)

def update_list(name: str):
    list_films = get_films_on_list(lb_lists[name])
    update_db_with_new_films(list_films)
    if list_is_in_db(name):
        update_db_list(name, convert_films_to_ids(list_films))
    else:
        add_list_to_db(name, convert_films_to_ids(list_films))

def get_films_on_list(url: str):

    async def inner():
        scraped_pages = await scrape_list(url)
        films = get_film_entries_from_scraped_pages(scraped_pages)
        return films

    asyncio.set_event_loop(asyncio.SelectorEventLoop())
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(inner())
    films = loop.run_until_complete(future)

    return films

