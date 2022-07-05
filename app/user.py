from app.database import query_user_attr, update_db_user_category, query_category_of_all_db_films, get_primary_key
from typing import Tuple, List, Union
from app.categories import DirectorStats, CountryStats, Category


def get_top_category_biased(username: str, category_type: str, nr_items: int = 10) -> List[list]:

    sorted_category = get_category_sorted_by_biased(username, category_type)
    top_category = []
    for i, category in zip(range(nr_items), sorted_category):
        name = category[1]
        avg_rating = round(category[2], 2)
        bias_rating = round(category[3], 2)
        nr_films = category[4]
        top_category.append([name, avg_rating, bias_rating, nr_films])

    return top_category


def get_category_sorted_by_biased(username: str, category_type: str) -> List[Tuple]:

    user_category = query_user_attr(username, category_type)
    if user_category is None:
        update_user_category(username, category_type)
        user_category = query_user_attr(username, category_type)

    sorted_category = sorted(user_category, key=lambda x: x[3], reverse=True)
    return sorted_category


def update_user_statistics(username: str) -> None:
    update_user_category(username, 'Director')
    update_user_category(username, 'Country')


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


def initialize_category(category_type, name) -> Category:

    if category_type == 'Director':
        return DirectorStats(name)
    elif category_type == 'Country':
        return CountryStats(name)
    else:
        return Category(name)


def add_attrs_to_category(categories: dict) -> List[Tuple]:

    categories_with_attrs = []
    for key in categories:
        category = categories[key]

        attrs = get_category_attrs(key, category)
        categories_with_attrs.append(attrs)

    return categories_with_attrs


def get_category_attrs(key: Union[int, str], category: Union[DirectorStats, CountryStats]) -> Tuple[Union[int, str], str, float, float, int]:

    name = category.name
    avg_rating = category.average_rating
    bias_rating = category.biased_rating
    nr_films = category.number_of_films

    return key, name, avg_rating, bias_rating, nr_films
