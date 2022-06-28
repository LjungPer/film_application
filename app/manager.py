import re
from bs4 import BeautifulSoup, SoupStrainer
from app.database import extract_films_not_in_db, add_films_to_db, user_in_db, add_user_to_db, update_db_user
from app.scraping import scrape_letterboxd_urls_of_films, scrape_pages_of_user_films_by_date, get_page_count, get_user_avatar_src
from app.models import User
import asyncio
from app.decorators import timed


def set_up_user(username):

    if not user_in_db(username):
        num_pages, avatar_url, logged_films = get_user_info(username)
        logged_films_compact = convert_logged_films_to_tuples(logged_films)
        add_user_to_db(username, logged_films_compact, num_pages, avatar_url)

def update_user_info(username, return_logged_films=False):

    num_pages, avatar_url, logged_films = get_user_info(username)
    logged_films_compact = convert_logged_films_to_tuples(logged_films)
    update_db_user(username, logged_films_compact, num_pages, avatar_url)
    if return_logged_films:
        return logged_films


def get_user_info(username):

    num_pages = get_page_count(username)
    avatar_url = get_user_avatar_src(username)
    logged_films = get_user_films(username) 

    return num_pages, avatar_url, logged_films


@timed
def get_user_films(username):

    async def inner():
        if user_in_db(username):
            u = User.query.get(username)
            num_pages = u.num_pages
        else:
            num_pages = get_page_count(username)
        pages_of_user_films_by_date = await scrape_pages_of_user_films_by_date(username, num_pages)
        user_films = get_user_films_from_scraped_pages(pages_of_user_films_by_date)
        return user_films

    asyncio.set_event_loop(asyncio.SelectorEventLoop())
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(inner())
    user_films = loop.run_until_complete(future)

    return user_films


def get_user_films_from_scraped_pages(scraped_pages):
    user_films = []
    for current_page in scraped_pages:
        entries_of_current_page = get_entries_of_current_page(current_page)

        for entry in entries_of_current_page:
            user_film = create_user_film_from_scraped_entry(entry)
            user_films.append(user_film)
    return user_films


def get_entries_of_current_page(page):
    soup = BeautifulSoup(page, "lxml")
    entries = soup.findAll("li", attrs={"class": "poster-container"})
    return entries


def create_user_film_from_scraped_entry(entry):
    film_entry = entry.find('div', attrs={"class", "film-poster"})
    rating_entry = entry.find("span", attrs={"class": "rating"})

    user_film = {"film_title": get_letterboxd_title(film_entry),
                 "letterboxd_id": get_letterboxd_id(film_entry),
                 "tmdb_id": None,
                 "rating": get_user_rating(rating_entry),
                 "url": get_letterboxd_url(film_entry),
                 "movie": None,
                 "tv": None}
    return user_film


def get_letterboxd_title(entry):
    return entry['data-target-link'].split('/')[-2]


def get_letterboxd_id(entry):
    return entry['data-film-id']


def get_user_rating(entry):
    if entry is None:
        return None
    else:
        rating_class = entry['class'][-1]
        rating = int(rating_class.split('-')[-1])
        return rating


def get_letterboxd_url(entry):
    url_append = entry['data-film-slug']
    url = "https://letterboxd.com{}".format(url_append)
    return url


def convert_logged_films_to_tuples(logged_films):

    films_compact = []
    for i in range(len(logged_films)):
        tup = (logged_films[i]['letterboxd_id'], logged_films[i]['rating'])
        films_compact.append(tup)
    return films_compact


def update_db_with_new_films(user_films):

    async def inner():
        scrape_responses = await scrape_letterboxd_urls_of_films(films_not_in_db)
        return scrape_responses

    films_not_in_db = extract_films_not_in_db(user_films)
    asyncio.set_event_loop(asyncio.SelectorEventLoop())
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(inner())
    scrape_responses = loop.run_until_complete(future)

    add_scraped_info_to(films_not_in_db, scrape_responses)
    add_films_to_db(films_not_in_db)


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
