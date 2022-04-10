from app.models import *
from app import objects

''' Suggestion: implement a class named User that simply has these attributes and functions. Should be more structured 
    than just random functions put into a file. '''


def generate_director_dictionary(user_films):
    # Only time consuming thing here is to query all films on first line.

    db_films = Film.query.all()
    db_film_director_dict = {film.letterboxd_id: film.director for film in db_films}
    director_dict = {}
    for film in user_films:
        if int(film['letterboxd_id']) in db_film_director_dict:
            directors = db_film_director_dict[int(film['letterboxd_id'])]
            for director in directors:
                if director.director_id in director_dict:
                    director_dict[director.director_id].add_film(film)
                else:
                    director_dict[director.director_id] = objects.Director(name=director.name)
                    director_dict[director.director_id].add_film(film)

    return director_dict


def sort_directors_by_biased_rating(director_dict):

    for key in director_dict:
        director_dict[key].compute_biased_rating()

    return {k: v for k, v in sorted(director_dict.items(), key = lambda item: item[1].biased_rating,
                                    reverse=True)}

def get_list_of_top_directors(sorted_directors, number):

    count = 0
    top_directors_list = []
    for key in list(sorted_directors):
        tmp = [sorted_directors[key].name, round(sorted_directors[key].biased_rating, 2)]
        top_directors_list.append(tmp)
        count += 1
        if count == number:
            break

    return top_directors_list