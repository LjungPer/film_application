import re
from bs4 import BeautifulSoup, SoupStrainer
from app.database import extract_films_not_in_db, add_films_to_db, query_user_attr, user_is_in_db, add_user_to_db, update_db_user
from app.scraping import scrape_letterboxd_urls_of_films, scrape_pages_of_user_films_by_date, get_page_count, get_user_avatar_src
import asyncio
from app.decorators import timed
from typing import List


def set_up_user(username):

    if not user_is_in_db(username):
        pages, avatar_url, logged_films = get_user_info(username)
        logged_films_compact = convert_logged_films_to_tuples(logged_films)
        add_user_to_db(username, logged_films_compact, pages, avatar_url)


def update_user_info(username, return_logged_films=False):

    num_pages, avatar_url, logged_films = get_user_info(username)
    logged_films_compact = convert_logged_films_to_tuples(logged_films)
    update_db_user(username, logged_films_compact, num_pages, avatar_url)
    if return_logged_films:
        return logged_films


def get_user_info(username):

    num_pages = get_page_count(username)
    avatar_url = get_user_avatar_src(username)
    logged_films = get_user_films(username, num_pages)

    return num_pages, avatar_url, logged_films


@timed
def get_user_films(username: str, num_pages: int) -> List[dict]:

    async def inner():
        pages_of_user_films_by_date = await scrape_pages_of_user_films_by_date(username, num_pages)
        user_films = get_user_films_from_scraped_pages(
            pages_of_user_films_by_date)
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
    for film in logged_films:
        id = int(film['letterboxd_id'])
        if film['rating'] is not None:
            rating = film['rating']
        else:
            rating = 'Not rated'
        tup = (id, rating)
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

    add_scraped_info(films_not_in_db, scrape_responses)
    add_films_to_db(films_not_in_db)


def add_scraped_info(films, scrape_responses):
    relevant = SoupStrainer(
        'a', attrs={"class": "micro-button track-event", "data-track-action": "TMDb"})
    for film, response in zip(films, scrape_responses):
        soup = BeautifulSoup(response, "lxml", parse_only=relevant)
        tmp = soup.find('a', attrs={
                        "class": "micro-button track-event", "data-track-action": "TMDb"})['href']  # type: ignore

        if re.search('movie/(.*)/', tmp) is not None:  # type: ignore
            tmdb_id = re.search('movie/(.*)/', tmp).group(1)  # type: ignore
            film['tmdb_id'] = tmdb_id
            film['movie'] = True

        if re.search('tv/(.*)/', tmp) is not None:  # type: ignore
            tmdb_id = re.search('tv/(.*)/', tmp).group(1)  # type: ignore
            film['tmdb_id'] = tmdb_id
            film['tv'] = True


def get_ratings_from_films(films):
    rated_films_from_year = [
        film for film in films if isinstance(film[2], int)]
    nr_rated_films = len(rated_films_from_year)
    ratings = [0] * 10
    avg_rating = 0
    for film in rated_films_from_year:
        ratings[film[2]-1] += 1
        avg_rating += film[2]
    avg_rating = round(avg_rating / nr_rated_films, 2)

    return ratings, avg_rating


def get_data_for_all_years(username):
    user_years = query_user_attr(username, 'Year')
    user_years = sorted(user_years, key=lambda x: int(x[0]), reverse=True)
    first_year = int(user_years[-1][0])
    last_year = int(user_years[0][0])
    all_years = list(range(first_year, last_year+1))
    yearly_data = {int(year[0]): (year[2], year[3], year[4])
                   for year in user_years}
    avg = []
    bias = []
    nr_films = []
    for year in all_years:
        if year in yearly_data:
            avg.append(yearly_data[year][0])
            bias.append(yearly_data[year][1])
            nr_films.append(yearly_data[year][2])
        else:
            avg.append(0)
            bias.append(0)
            nr_films.append(0)
    return all_years, avg, bias, nr_films
