from bs4 import BeautifulSoup, SoupStrainer
import re
import requests
import asyncio
from aiohttp import ClientSession
from app.decorators import timed
from typing import List, Tuple, Union


@timed
def get_user_avatar_src(username):
    user_url = "https://letterboxd.com/{}/"
    r = requests.get(user_url.format(username))
    soup = BeautifulSoup(r.text, "lxml")
    avatar_url = soup.findAll('img')[0]['src']
    return avatar_url


async def scrape_letterboxd_urls_of_films(films):
    async with ClientSession() as session:
        tasks = []
        for film in films:
            task = asyncio.ensure_future(fetch(film['url'], session))
            tasks.append(task)

        scrape_responses = await asyncio.gather(*tasks)
    return scrape_responses


async def fetch(url, session):
    async with session.get(url) as response:
        return await response.read()

@timed
async def scrape_list(list_url: str):
    num_pages = get_page_count_from_url(list_url)
    url = list_url + 'page/{}'
    scraped_pages = await scrape_pages(url, num_pages)
    return scraped_pages

@timed
async def scrape_user_films(username: str, num_pages: int):
    url = "https://letterboxd.com/{}/films/by/date/page/{}"
    scraped_pages = await scrape_pages(url, num_pages, username)
    return scraped_pages

@timed
async def scrape_user_diary(username: str, num_pages: int):
    url = 'https://letterboxd.com/{}/films/diary/page/{}'
    scraped_pages = await scrape_pages(url, num_pages, username)
    return scraped_pages

@timed
async def scrape_pages(url: str, num_pages: int, username: str=''):

    async with ClientSession() as session:
        tasks = []

        for i in range(num_pages):
            if username == '':
                task = asyncio.ensure_future(fetch(url.format(i+1), session))
            else:
                task = asyncio.ensure_future(fetch(url.format(username, i+1), session))
            tasks.append(task)

        scraped_pages = await asyncio.gather(*tasks)

    return scraped_pages

def get_film_entries_from_scraped_pages(scraped_pages) -> List[dict]:
    entries = []
    for current_page in scraped_pages:
        entries_of_current_page = get_film_entries_of_page(current_page)

        for entry in entries_of_current_page:
            film = create_film_from_scraped_entry(entry)
            entries.append(film)

    return entries

def get_diary_entries_from_scraped_pages(scraped_pages) -> List[Tuple]:
    entries = []
    for current_page in scraped_pages:
        entries_of_current_page = get_diary_entries_of_page(current_page)

        for entry in entries_of_current_page:
            diary_entry = create_diary_entry_from_scraped_entry(entry)
            entries.append(diary_entry)

    return entries

def get_film_entries_of_page(page):
    soup = BeautifulSoup(page, 'lxml')
    return soup.findAll('li', attrs={'class': 'poster-container'})

def get_diary_entries_of_page(page):
    soup = BeautifulSoup(page, 'lxml')
    return soup.findAll('a', attrs={'class': 'edit-review-button has-icon icon-16 icon-edit'})

def create_film_from_scraped_entry(entry):
    film_entry = entry.find('div', attrs={"class", "film-poster"})
    rating_entry = entry.find("span", attrs={"class": "rating"})

    film = {"film_title": get_letterboxd_title(film_entry),
            "letterboxd_id": get_letterboxd_id(film_entry),
            "tmdb_id": None,
            "rating": get_user_rating(rating_entry),
            "url": get_letterboxd_url(film_entry),
            "movie": None,
            "tv": None}
    return film

def create_diary_entry_from_scraped_entry(entry) -> Tuple:
    letterboxd_id = int(entry['data-film-id'])
    title = entry['data-film-name']
    rewatch = 1 if entry['data-rewatch'] == 'true' else 0
    date = entry['data-viewing-date']
    reviewed = 0 if entry['data-review-text'] == "" else 1
    return (letterboxd_id, title, rewatch, date, reviewed)

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

def get_page_count_from_url(url: str) -> int:
    
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")

    body = soup.find("body")
    if "error" in body['class']:  # type: ignore
        return -1

    try:
        # find_all finds all instances of a tag on a page
        page_link = soup.findAll("li", attrs={"class", "paginate-page"})[-1]
        num_pages = int(page_link.find("a").text.replace(',', ''))
    except IndexError:
        # There is no bar if there is only one page
        num_pages = 1

    return num_pages


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
