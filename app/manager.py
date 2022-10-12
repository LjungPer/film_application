from app.database import query_user_attr, query_member_from_category_by_id
from typing import List, Tuple, Union

def convert_films_to_ids(films, include_rating=False):
    ids = []
    for film in films:
        id = int(film['letterboxd_id'])
        if include_rating:
            rating = extract_rating(film)
            id = (id, rating)
        ids.append(id)
    return ids

def extract_rating(film: dict) -> Union[int, str]:
    if film['rating'] is not None:
        return film['rating']
    else:
        return 'Not rated'

def get_ratings_from_films(films):
    rated_films_from_year = [
        film for film in films if isinstance(film[2], int)]
    nr_rated_films = len(rated_films_from_year)
    ratings = [0] * 10
    avg_rating = 0
    for film in rated_films_from_year:
        ratings[film[2]-1] += 1
        avg_rating += film[2]
    avg_rating = round(avg_rating / nr_rated_films, 2)

    return ratings, avg_rating

def get_data_for_all_years(username):
    user_years = query_user_attr(username, 'Year')
    user_years = sorted(user_years, key=lambda x: int(x[0]), reverse=True)
    first_year = int(user_years[-1][0])
    last_year = int(user_years[0][0])
    all_years = list(range(first_year, last_year+1))
    yearly_data = {int(year[0]): (year[2], year[3], year[4])
                   for year in user_years}
    avg = []
    bias = []
    nr_films = []
    for year in all_years:
        if year in yearly_data:
            avg.append(yearly_data[year][0])
            bias.append(yearly_data[year][1])
            nr_films.append(yearly_data[year][2])
        else:
            avg.append(0)
            bias.append(0)
            nr_films.append(0)
    return all_years, avg, bias, nr_films

def get_data_for_all_of_category(username: str, category: str):
    user_category = query_user_attr(username, category)
    avg = sorted(user_category, key=lambda x: float(x[2]), reverse=True)
    bias = sorted(user_category, key=lambda x: float(x[3]), reverse=True)
    nr_films = sorted(user_category, key=lambda x: int(x[4]), reverse=True)
            
    return avg, bias, nr_films

def get_top(d: dict, category: str, n: int=5) -> List[Tuple]:
    d = sort_dictionary(d)
    top = []
    for (key, _) in zip(d, range(n)):
        if category in ['Director', 'Actor', 'Actress']:
            member = query_member_from_category_by_id(category, key)
            name = member.name
            avatar_url = member.avatar_url
            top.append((name, d[key], avatar_url))
        else:
            top.append((key, d[key]))
    return top

def sort_dictionary(d: dict) -> dict:
    return dict(sorted(d.items(), key=lambda item: item[1], reverse=True))