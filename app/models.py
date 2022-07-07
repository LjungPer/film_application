from app import db


director_film_table = db.Table('director_film',
                               db.Column('letterboxd_id', db.Integer,
                                         db.ForeignKey('film.letterboxd_id')),
                               db.Column('id', db.Integer, db.ForeignKey('director.id')))


country_film_table = db.Table('country_film',
                              db.Column('letterboxd_id', db.Integer,
                                        db.ForeignKey('film.letterboxd_id')),
                              db.Column('name', db.Integer, db.ForeignKey('country.name')))


year_film_table = db.Table('year_film',
                           db.Column('letterboxd_id', db.Integer,
                                     db.ForeignKey('film.letterboxd_id')),
                           db.Column('name', db.Integer, db.ForeignKey('year.name')))


actor_film_table = db.Table('actor_film',
                            db.Column('letterboxd_id', db.Integer,
                                      db.ForeignKey('film.letterboxd_id')),
                            db.Column('id', db.Integer, db.ForeignKey('actor.id')))


actress_film_table = db.Table('actress_film',
                              db.Column('letterboxd_id', db.Integer,
                                        db.ForeignKey('film.letterboxd_id')),
                              db.Column('id', db.Integer, db.ForeignKey('actress.id')))

genre_film_table = db.Table('genre_film',
                            db.Column('letterboxd_id', db.Integer,
                                      db.ForeignKey('film.letterboxd_id')),
                            db.Column('name', db.Integer, db.ForeignKey('genre.name')))


class Country(db.Model):
    name = db.Column(db.String(64), primary_key=True)

    def __repr__(self):
        return '<Country {}>'.format(self.name)

class Genre(db.Model):
    name = db.Column(db.String(64), primary_key=True)

    def __repr__(self):
        return '<Country {}>'.format(self.name)

class Actor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    def __repr__(self):
        return '<Actor {}>'.format(self.name)


class Actress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    def __repr__(self):
        return '<Actress {}>'.format(self.name)


class Year(db.Model):
    name = db.Column(db.String(16), primary_key=True)

    def __repr__(self):
        return '<Year {}>'.format(self.name)


class Director(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    def __repr__(self):
        return '<Director {}>'.format(self.name)


class Film(db.Model):
    letterboxd_id = db.Column(db.Integer, primary_key=True)
    tmdb_id = db.Column(db.Integer, index=True, unique=True)
    title = db.Column(db.String(128))
    director = db.relationship(
        'Director', secondary=director_film_table, backref=db.backref('films', lazy='dynamic'))
    country = db.relationship(
        'Country', secondary=country_film_table, backref=db.backref('films', lazy='dynamic'))
    year = db.relationship(
        'Year', secondary=year_film_table, backref=db.backref('films', lazy='dynamic'))
    actor = db.relationship(
        'Actor', secondary=actor_film_table, backref=db.backref('films', lazy='dynamic'))
    actress = db.relationship(
        'Actress', secondary=actress_film_table, backref=db.backref('films', lazy='dynamic'))
    genre = db.relationship(
        'Genre', secondary=genre_film_table, backref=db.backref('films', lazy='dynamic'))

    def __repr__(self):
        return '<Film {}>'.format(self.title)


class Tv(db.Model):
    letterboxd_id = db.Column(db.Integer, primary_key=True)
    tmdb_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))

    def __repr__(self):
        return '<TV {}>'.format(self.title)


class Miscellaneous(db.Model):
    letterboxd_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))

    def __repr__(self):
        return '<Misc {}>'.format(self.title)


class User(db.Model):
    username = db.Column(db.String(128), primary_key=True)
    films = db.Column(db.PickleType)
    num_pages = db.Column(db.Integer)
    avatar_url = db.Column(db.String(128))
    directors = db.Column(db.PickleType)
    countries = db.Column(db.PickleType)
    years = db.Column(db.PickleType)
    actors = db.Column(db.PickleType)
    actresses = db.Column(db.PickleType)
    genres = db.Column(db.PickleType)

    def __repr__(self):
        return '<User {}>'.format(self.username)
