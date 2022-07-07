from typing import List, Tuple
from app.database import query_user_attr
from app.user import update_user_category

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