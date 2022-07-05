from typing import Tuple


class Category:
    def __init__(self, name: str) -> None:
            self._name = name
            self._average_rating = None
            self._biased_rating = None
            self.films = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def average_rating(self) -> float:

        if self._average_rating is None:
            self._average_rating = round(self.compute_average_rating(), 2)
        return self._average_rating

    @property
    def biased_rating(self) -> float:
        if self._biased_rating is None:
            self._biased_rating = round(self.compute_biased_rating(), 2)
        return self._biased_rating

    @property
    def number_of_films(self) -> int:
        return len(self.films)

    def append_film(self, film: Tuple[int, int]) -> None:
        """
        Append a film to list of related films.

        Argument film characterized by tuple of attributes.
        film[0]: id(int), film[1]: rating(int).

        Parameters
        ----------
        film : Tuple[int, int]
            Film to append.
        """
        self.films.append(film)

    def compute_average_rating(self) -> float:
        tot_rating = 0
        nr_rated_films = 0
        for film in self.films:
            rating = film[1]
            if rating is not None:
                tot_rating += rating
                nr_rated_films += 1
        if nr_rated_films > 0:
            return tot_rating / nr_rated_films
        else:
            return 0

    def compute_biased_rating(self) -> float:
        nr_films = len(self.films)
        biased_factor = 1 - 0.8 / nr_films

        return self.average_rating * biased_factor



class Director(Category):
    def __init__(self, name: str) -> None:
        super().__init__(name)


class Country(Category):
    def __init__(self, name: str) -> None:
        super().__init__(name)
    