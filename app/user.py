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
