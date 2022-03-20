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