from bs4 import BeautifulSoup, SoupStrainer
import requests
import asyncio
from aiohttp import ClientSession
import time

async def fetch(url, session):
    async with session.get(url) as response:
        return await response.read()


def get_page_count(username):
    url = "https://letterboxd.com/{}/films/by/date"
    r = requests.get(url.format(username))      # Make GET request to download HTML content from url

    # Possibility to check if r.status_code = 200 (= page download successfully)
    # username="kattihatt2" returns <Response [200]> while "kattihatt3" gives <Response [404]>

    soup = BeautifulSoup(r.text, "lxml")

    body = soup.find("body")
    if "error" in body["class"]:
        return -1

    try:
        # find_all finds all instances of a tag on a page
        page_link = soup.findAll("li", attrs={"class", "paginate-page"})[-1]
        num_pages = int(page_link.find("a").text.replace(',', ''))
    except IndexError:
        # There is no bar if there is only one page
        num_pages = 1

    return num_pages


async def get_user_ratings(username, num_pages):

    url = "https://letterboxd.com/{}/films/by/date/page/{}"

    start = time.time()
    async with ClientSession() as session:
        tasks = []

        for i in range(num_pages):
            task = asyncio.ensure_future(fetch(url.format(username, i+1), session))
            tasks.append(task)

        scrape_responses = await asyncio.gather(*tasks)
    end = time.time()
    print("Time to get scrape responses i {time}".format(time=end-start))

    film_objects = []
    for response in scrape_responses:
        soup = BeautifulSoup(response, "lxml")
        posts = soup.findAll("li", attrs={"class": "poster-container"})

        for post in posts:
            tmp = post.find('div', attrs={"class", "film-poster"})
            film_title = tmp['data-target-link'].split('/')[-2]
            letterboxd_id = tmp['data-film-id']

            url_append = tmp['data-film-slug']

            url = "https://letterboxd.com{}".format(url_append)

            rating = post.find("span", attrs={"class": "rating"})
            if rating is None:
                rating_val = None
            else:
                rating_class = rating['class'][-1]
                rating_val = int(rating_class.split('-')[-1])

            film_object = {
                "film_title": film_title,
                "letterboxd_id": letterboxd_id,
                "tmdb_id": None,
                "rating": rating_val,
                "url": url,
                "movie": None,
                "tv": None
            }
            film_objects.append(film_object)

    return film_objects