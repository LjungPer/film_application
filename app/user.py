import asyncio
from app.manager import get_user_films
from app.decorators import timed
from app.database import get_directors_of_films

class User:
    def __init__(self, username):
        self._username = username

    @property
    def username(self):
        return self._username

    def get_top_directors(self, number=10):
        count = 0
        top_directors_list = []
        for key in list(self.sorted_directors):
            tmp = [self.sorted_directors[key].name, round(self.sorted_directors[key].biased_rating, 2)]
            top_directors_list.append(tmp)
            count += 1
            if count == number:
                break

        return top_directors_list

    @property
    def sorted_directors(self):
        if not hasattr(self, '_sorted_directors'):
            self._sorted_directors = sort_directors_by_biased_rating(self.directors)
        return self._sorted_directors

    @property
    def directors(self):
        if not hasattr(self, '_directors'):
            self._directors = create_director_dictionary(self.logged_films)
        return self._directors

    @property
    def logged_films(self):
        if not hasattr(self, '_logged_films'):
            async def inner():
                return await get_user_films(self.username)
            asyncio.set_event_loop(asyncio.SelectorEventLoop())
            loop = asyncio.get_event_loop()
            future = asyncio.ensure_future(inner())
            self._logged_films = loop.run_until_complete(future)
        return self._logged_films

    @logged_films.setter
    def logged_films(self, user_films):
        self._logged_films = user_films


''' Help with this function... Variable names, structure etc. '''
@timed
def create_director_dictionary(user_films):
    db_director_of_db_film = get_directors_of_films()
    user_directors = {}
    for film in user_films:
        if int(film['letterboxd_id']) in db_director_of_db_film:
            directors = db_director_of_db_film[int(film['letterboxd_id'])]
            for director in directors:
                if director.director_id in user_directors:
                    user_directors[director.director_id].add_film(film)
                else:
                    user_directors[director.director_id] = Director(name=director.name)
                    user_directors[director.director_id].add_film(film)

    return user_directors


def sort_directors_by_biased_rating(director_dict):

    for key in director_dict:
        director_dict[key].compute_biased_rating()

    return {k: v for k, v in sorted(director_dict.items(), key=lambda item: item[1].biased_rating,
                                    reverse=True)}



class Director:
    def __init__(self, name):
        self.name = name
        self.films = []
        self.average_rating = None
        self.biased_rating = None

    def get_name(self):
        return self.name

    def get_average_rating(self):
        return self.average_rating

    def get_biased_rating(self):
        return self.biased_rating

    def add_film(self, Film):
        self.films.append(Film)

    def print_films(self):
        for film in self.films:
            print('%s  %s' %(film.title, film.rating))

    def compute_average_rating(self):
        tot_rating = 0
        no_rated_films = 0
        for film in self.films:
            if film['rating'] is not None:
                tot_rating += int(film['rating'])
                no_rated_films += 1
        if no_rated_films > 0:
            self.average_rating = tot_rating / no_rated_films
        else:
            self.average_rating = 0

    def compute_biased_rating(self):
        self.compute_average_rating()
        no_films = len(self.films)
        biased_factor = 1 - 0.8 / no_films

        self.biased_rating = self.average_rating * biased_factor