from bs4 import BeautifulSoup
import requests
import asyncio
from aiohttp import ClientSession
from app.decorators import timed


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
async def scrape_pages_of_user_films_by_date(username, num_pages):

    url = "https://letterboxd.com/{}/films/by/date/page/{}"
    async with ClientSession() as session:
        tasks = []

        for i in range(num_pages):
            task = asyncio.ensure_future(fetch(url.format(username, i+1), session))
            tasks.append(task)

        scraped_pages = await asyncio.gather(*tasks)
    return scraped_pages


@timed
async def scrape_user_diary_pages(username, num_pages):

    url = 'https://letterboxd.com/{}/films/diary/page/{}'

    async with ClientSession() as session:
        tasks = []

        for i in range(num_pages):
            task = asyncio.ensure_future(fetch(url.format(username, i+1), session))
            tasks.append(task)

        scraped_pages = await asyncio.gather(*tasks)
    return scraped_pages


@timed
def get_user_avatar_src(username):
    user_url = "https://letterboxd.com/{}/"
    r = requests.get(user_url.format(username))
    soup = BeautifulSoup(r.text, "lxml")
    avatar_url = soup.findAll('img')[0]['src']
    return avatar_url


@timed
def get_films_page_count(username):
    url = "https://letterboxd.com/{}/films/by/date"
    num_pages = get_page_count_from_url(url.format(username))
    return num_pages


@timed
def get_diary_page_count(username):
    url = 'https://letterboxd.com/{}/films/diary/'
    num_pages = get_page_count_from_url(url.format(username))
    return num_pages


def get_page_count_from_url(url):
    
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