from app.database import query_user_attr, update_db_user_category, query_category_of_all_db_films, get_primary_key
from typing import Tuple, List, Union
from app.categories import Director, Country, Category


def get_top_directors_biased(username: str, nr_items: int = 10) -> List[list]:
    """
    Return list of top directors based on biased rating.

    Each director in list is represented by a list of attributes.
    Attributes consist of name(str), avg_rating(float),  bias_rating(float) and nr_films(int).

    Parameters
    ----------
    username : str

    no_items : int, optional
        Number of directors to be returned, by default 10.

    Returns
    -------
    List[list]
        List of top directors based on biased rating.
    """
    sorted_directors = get_directors_sorted_by_biased(username)
    top_directors = []
    for i, director in zip(range(nr_items), sorted_directors):
        name = director[1]
        avg_rating = round(director[2], 2)
        bias_rating = round(director[3], 2)
        nr_films = director[4]
        top_directors.append([name, avg_rating, bias_rating, nr_films])

    return top_directors


def get_directors_sorted_by_biased(username: str) -> List[Tuple]:
    user_directors = query_user_attr(username, 'Director')
    if user_directors is None:
        update_user_category_statistics(username, 'Director')
        user_directors = query_user_attr(username, 'Director')

    sorted_directors = sorted(user_directors, key=lambda x: x[3], reverse=True)
    return sorted_directors


def update_user_statistics(username: str) -> None:
    update_user_category_statistics(username, 'Director')
    update_user_category_statistics(username, 'Country')


def update_user_category_statistics(username: str, category_type: str) -> None:
    user_category = collect_category(username, category_type)
    category_with_attrs = add_attrs_to_category(user_category)
    update_db_user_category(username, category_with_attrs, category_type)


def collect_category(username: str, category: str) -> dict:

    db_category_of_db_film = query_category_of_all_db_films(category)
    user_films = query_user_films(username)
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
                        category, db_category.name)
                    user_categories[primary_key].append_film(film)

    return user_categories


def initialize_category(category, name) -> Category:

    if category == 'Director':
        return Director(name)
    elif category == 'Country':
        return Country(name)
    else:
        return Category(name)


def add_attrs_to_category(categories: dict) -> List[Tuple]:

    categories_with_attrs = []
    for key in categories:
        category = categories[key]

        attrs = get_category_attrs(key, category)
        categories_with_attrs.append(attrs)

    return categories_with_attrs


def get_category_attrs(key: Union[int, str], category: Union[Director, Country]) -> Tuple[Union[int, str], str, float, float, int]:

    name = category.name
    avg_rating = category.average_rating
    bias_rating = category.biased_rating
    nr_films = category.number_of_films

    return key, name, avg_rating, bias_rating, nr_films
