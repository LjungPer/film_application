from app.database import query_user_attr, update_db_user_category, query_category_of_all_db_films, get_primary_key
from typing import Tuple, List, Union, overload
from app.categories import *


def update_user_statistics(username: str) -> None:
    update_user_category(username, 'Director')
    update_user_category(username, 'Country')
    update_user_category(username, 'Year')
    update_user_category(username, 'Actor')
    update_user_category(username, 'Actress')
    update_user_category(username, 'Genre')


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
                    user_categories[primary_key] = initialize_category(
                        category_type, db_category.name)
                    user_categories[primary_key].append_film(film)

    return user_categories


def initialize_category(category_type: str, name: str) -> Category:

    if category_type == 'Director':
        return DirectorStats(name)
    elif category_type == 'Country':
        return CountryStats(name)
    elif category_type == 'Year':
        return YearStats(name)
    elif category_type == 'Actor':
        return ActorStats(name)
    elif category_type == 'Actress':
        return ActressStats(name)
    elif category_type == 'Genre':
        return GenreStats(name)
    else:
        return Category(name)


def add_attrs_to_category(categories: dict) -> List[Tuple]:

    categories_with_attrs = []
    for key in categories:
        category = categories[key]

        attrs = get_category_attrs(key, category)
        categories_with_attrs.append(attrs)

    return categories_with_attrs


@overload
def get_category_attrs(key: int, category: Union[DirectorStats, ActorStats, ActressStats]) -> Tuple[int, str, float, float, int]:
    ...


@overload
def get_category_attrs(key: str, category: Union[CountryStats, YearStats, GenreStats]) -> Tuple[str, str, float, float, int]:
    ...


def get_category_attrs(key: Union[int, str], category: Category) -> Tuple[Union[int, str], str, float, float, int]:

    name = category.name
    avg_rating = category.average_rating
    bias_rating = category.biased_rating
    nr_films = category.number_of_films

    return key, name, avg_rating, bias_rating, nr_films

from app.models import *
def get_user_films_from_year(username: str, year: str):
    u = User.query.get(username)
    y = Year.query.get(year)

    user_film_ids = {id for (id,_) in u.films}
    year_film_ids = {film.letterboxd_id for film in y.films}

    user_film_ids_this_year = set.intersection(user_film_ids, year_film_ids)
    user_films_this_year = [(Film.query.get(film[0]).title, film[0], film[1]) for film in u.films if film[0] in user_film_ids_this_year]
    return user_films_this_year