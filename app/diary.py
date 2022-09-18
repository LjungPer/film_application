
import re
from this import d
from bs4 import BeautifulSoup, SoupStrainer
from app.database import DatabaseType, extract_films_not_in_db, add_films_to_db, get_primary_key, query_user_attr, update_db_user_category, user_is_in_db, add_user_to_db, update_db_user, query_film
from app.scraping import scrape_letterboxd_urls_of_films, scrape_pages_of_user_films_by_date, get_films_page_count, get_user_avatar_src, get_diary_page_count, scrape_user_diary_pages
import asyncio
from app.decorators import timed
from typing import List, Tuple
import pandas as pd
import datetime
import calendar
from app.manager import sort_dictionary



def update_user_diary(username: str):
    diary = get_diary_entries(username)
    update_db_user_category(username, diary, 'Diary')


def get_diary_info_from_year(username: str, year: int):
    diary = query_user_attr(username, 'Diary')
    yearly_diary = extract_yearly_diary_data(diary)
    weekday_films, weekly_films, monthly_films = get_watched_films_statistics_of_year(yearly_diary, year)
    return weekday_films, weekly_films, monthly_films


def get_all_diary_info_from_year(username: str, year_of_choice: int):
    diary = query_user_attr(username, 'Diary')
    yearly_diary = extract_yearly_diary_data(diary)

    directors = get_category_diary_data_from_year(yearly_diary, year_of_choice, 'Director')
    years = get_category_diary_data_from_year(yearly_diary, year_of_choice, 'Year')
    actors = get_category_diary_data_from_year(yearly_diary, year_of_choice, 'Actor')
    actresses = get_category_diary_data_from_year(yearly_diary, year_of_choice, 'Actress')
    countries = get_category_diary_data_from_year(yearly_diary, year_of_choice, 'Country')
    languages = get_category_diary_data_from_year(yearly_diary, year_of_choice, 'Language')
    genres = get_category_diary_data_from_year(yearly_diary, year_of_choice, 'Genre')

    return directors, years, actors, actresses, genres, languages, countries


def get_category_diary_data_from_year(yearly_diary: dict, year: int, category_type: str) -> dict:
    category = {}
    for entry in yearly_diary[year]:
        film_id = entry[0]
        film = query_film(film_id)
        film_category = getattr(film, category_type.lower())

        category = add_to_category(film_category, category)
    
    return sort_dictionary(category)


def add_to_category(members: list, category: dict) -> dict:
    for member in members:
        primary_key = get_primary_key(member)
        if primary_key in category:
            category[primary_key] += 1
        else:
            category[primary_key] = 1
    return category

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