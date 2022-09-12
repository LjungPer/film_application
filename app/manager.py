import re
from bs4 import BeautifulSoup, SoupStrainer
from app.database import extract_films_not_in_db, add_films_to_db, query_user_attr, update_db_user_category, user_is_in_db, add_user_to_db, update_db_user
from app.scraping import scrape_letterboxd_urls_of_films, scrape_pages_of_user_films_by_date, get_films_page_count, get_user_avatar_src, get_diary_page_count, scrape_user_diary_pages
import asyncio
from app.decorators import timed
from typing import List, Tuple
import pandas as pd
import datetime
import calendar


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

    num_pages = get_films_page_count(username)
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

def get_data_for_all_of_category(username: str, category: str):
    user_category = query_user_attr(username, category)
    avg = sorted(user_category, key=lambda x: float(x[2]), reverse=True)
    bias = sorted(user_category, key=lambda x: float(x[3]), reverse=True)
    nr_films = sorted(user_category, key=lambda x: int(x[4]), reverse=True)
            
    return avg, bias, nr_films

def update_user_diary(username: str):
    diary = get_diary_entries(username)
    update_db_user_category(username, diary, 'Diary')


def get_diary_info_from_year(username: str, year: int):
    diary = query_user_attr(username, 'Diary')
    yearly_diary = extract_yearly_diary_data(diary)
    weekday_films, weekly_films, monthly_films = get_watched_films_statistics_of_year(yearly_diary, year)
    return weekday_films, weekly_films, monthly_films


def get_diary_entries(username: str) -> List[Tuple]:
    num_pages = get_diary_page_count(username)

    async def inner():
        scraped_diary_pages = await scrape_user_diary_pages(username, num_pages)
        user_diary_entries = get_user_diary_entries_from_scraped_pages(scraped_diary_pages)
        return user_diary_entries

    asyncio.set_event_loop(asyncio.SelectorEventLoop())
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(inner())
    user_diary_entries = loop.run_until_complete(future)

    return user_diary_entries


def get_user_diary_entries_from_scraped_pages(scraped_pages) -> List[Tuple]:
    user_diary_entries = []
    for current_page in scraped_pages:
        entries_of_current_page = get_entries_of_diary_page(current_page)

        for entry in entries_of_current_page:
            user_diary_entry = create_user_diary_entry_from_scraped_entry(entry)
            user_diary_entries.append(user_diary_entry)
    return user_diary_entries


def get_entries_of_diary_page(page):
    soup = BeautifulSoup(page, 'lxml')
    return soup.findAll('a', attrs={'class': 'edit-review-button has-icon icon-16 icon-edit'})


def create_user_diary_entry_from_scraped_entry(entry) -> Tuple:
    letterboxd_id = int(entry['data-film-id'])
    title = entry['data-film-name']
    rewatch = 1 if entry['data-rewatch'] == 'true' else 0
    date = entry['data-viewing-date']
    reviewed = 0 if entry['data-review-text'] == "" else 1
    return (letterboxd_id, title, rewatch, date, reviewed)

def extract_yearly_diary_data(diary):
    diary_by_year = {}
    for entry in diary:
        year_of_entry = get_year_of_diary_entry(entry)
        if year_of_entry in diary_by_year:
            diary_by_year[year_of_entry].append(entry)
        else:
            diary_by_year[year_of_entry] = [entry]
    return diary_by_year


def get_year_of_diary_entry(entry):
    date_string = entry[3] # date, e.g. '2022-01-15'
    year = int(date_string.split("-")[0])
    return year


def get_watched_films_statistics_of_year(diary: dict, year: int) -> Tuple[List[int], List[int], List[int]]:
    diary_entries_of_the_year = diary[year]
    weekday_films = [0] * 7
    weekly_films = [0] * (number_of_weeks_of_year(year) + 1)
    monthly_films = [0] * 12
    for entry in diary_entries_of_the_year:

        date = entry[3]
        day, week, month = convert_date_string_to_ints(date)

        weekday_films[day] += 1
        if month == 1 and week > 50:
            weekly_films[0] += 1
        else:
            weekly_films[week] += 1
        monthly_films[month - 1] += 1
    
    return weekday_films, weekly_films, monthly_films


def convert_date_string_to_ints(date: str) -> Tuple[int, int, int]:
    timestamp = pd.Timestamp(date)
    day = timestamp.dayofweek
    week = timestamp.week
    month = timestamp.month
    return day, week, month

        
def number_of_weeks_of_year(year: int) -> int:
    first_day = datetime.datetime(year, 1, 1).weekday()
    if calendar.isleap(year) and first_day == 2:
        return 53
    if first_day == 3:
        return 53
    return 52

def get_basic_data_from_year(username: str, year: int) -> Tuple[int, int, int, list]:
    diary = query_user_attr(username, 'Diary')
    yearly_diary = extract_yearly_diary_data(diary)
    nr_films = len(yearly_diary[year])
    nr_reviews = 0
    nr_rewatches = 0
    nr_watches_per_film = {}
    for entry in yearly_diary[year]:
        nr_reviews += entry[4]
        nr_rewatches += entry[2]

        id = entry[0]
        if id in nr_watches_per_film:
            nr_watches_per_film[id] += 1
        else:
            nr_watches_per_film[id] = 1

    nr_watches_per_film = dict(sorted(nr_watches_per_film.items(), key=lambda item: item[1], reverse=True))
    top_five_watched_films = []
    for key in nr_watches_per_film:
        top_five_watched_films.append((key, nr_watches_per_film[key]))
        if len(top_five_watched_films) == 5:
            break

    return nr_films, nr_rewatches, nr_reviews, top_five_watched_films
