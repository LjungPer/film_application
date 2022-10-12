from app.database import query_user_attr, update_db_user_category, query_category_of_all_db_films, get_primary_key
from app.database import user_is_in_db, add_user_to_db, update_db_user
from app.manager import convert_films_to_ids
from typing import Tuple, List, Union
import asyncio
from app.decorators import timed
from app.categories import *
from app.scraping import get_film_entries_from_scraped_pages, get_page_count_from_url, get_user_avatar_src, scrape_user_films


def set_up_user(username):

    if not user_is_in_db(username):
        pages, avatar_url, logged_films = get_user_info(username)
        logged_films_compact = convert_films_to_ids(logged_films, include_rating=True)
        add_user_to_db(username, logged_films_compact, pages, avatar_url)

def update_user_info(username, return_logged_films=False):

    num_pages, avatar_url, logged_films = get_user_info(username)
    logged_films_compact = convert_films_to_ids(logged_films, include_rating=True)
    update_db_user(username, logged_films_compact, num_pages, avatar_url)
    if return_logged_films:
        return logged_films

def get_user_info(username):

    url = "https://letterboxd.com/{}/films/by/date"
    num_pages = get_page_count_from_url(url.format(username))
    avatar_url = get_user_avatar_src(username)
    logged_films = get_user_films(username, num_pages)

    return num_pages, avatar_url, logged_films

@timed
def get_user_films(username: str, num_pages: int) -> List[dict]:

    async def inner():
        pages_of_user_films_by_date = await scrape_user_films(username, num_pages)
        user_films = get_film_entries_from_scraped_pages(pages_of_user_films_by_date)
        return user_films

    asyncio.set_event_loop(asyncio.SelectorEventLoop())
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(inner())
    user_films = loop.run_until_complete(future)

    return user_films

def update_user_statistics(username: str) -> None:
    update_user_category(username, 'Director')
    update_user_category(username, 'Country')
    update_user_category(username, 'Year')
    update_user_category(username, 'Actor')
    update_user_category(username, 'Actress')
    update_user_category(username, 'Genre')
    update_user_category(username, 'Language')

def update_user_category(username: str, category_type: str) -> None:
    user_category = collect_category(username, category_type)
    category_with_attrs = add_attrs_to_category(user_category)
    update_db_user_category(username, category_with_attrs, category_type)

def collect_category(username: str, category_type: str) -> dict:

    db_category_of_db_film = query_category_of_all_db_films(category_type)
    user_films = query_user_attr(username, 'Film')
    user_categories = {}
    for film in user_films:
        index_of_film = film[0]
        if index_of_film in db_category_of_db_film:
            db_categories = db_category_of_db_film[index_of_film]
            for db_category in db_categories:
                primary_key = get_primary_key(db_category)
                if primary_key in user_categories:
                    user_categories[primary_key].append_film(film)
                else:
                    user_categories[primary_key] = Category(db_category.name)
                    user_categories[primary_key].append_film(film)

    return user_categories

def add_attrs_to_category(categories: dict) -> List[Tuple]:

    categories_with_attrs = []
    for key in categories:
        category = categories[key]

        attrs = get_category_attrs(key, category)
        categories_with_attrs.append(attrs)

    return categories_with_attrs

def get_category_attrs(key: Union[int, str], category: Category) -> Tuple[Union[int, str], str, float, float, int]:

    name = category.name
    avg_rating = category.average_rating
    bias_rating = category.biased_rating
    nr_films = category.number_of_films

    return key, name, avg_rating, bias_rating, nr_films

    