from app import db

director_film_table = db.Table('director_film',
                               db.Column('letterboxd_id', db.Integer, db.ForeignKey('film.letterboxd_id')),
                               db.Column('director_id', db.Integer, db.ForeignKey('director.director_id')))


class Director(db.Model):
    ''' rename director_id to e.g. letterboxd_id or just id '''
    director_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    def __repr__(self):
        return '<Director {}>'.format(self.name)


class Film(db.Model):
    letterboxd_id = db.Column(db.Integer, primary_key=True)
    tmdb_id = db.Column(db.Integer, index=True, unique=True)
    title = db.Column(db.String(128))
    director = db.relationship('Director', secondary=director_film_table, backref=db.backref('films', lazy='dynamic'))

    def __repr__(self):
        return '<Film {}>'.format(self.title)


class Tv(db.Model):
    letterboxd_id = db.Column(db.Integer, primary_key=True)
    tmdb_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))

    def __repr__(self):
        return '<Film {}>'.format(self.title)


class Miscellaneous(db.Model):
    letterboxd_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))

    def __repr__(self):
        return '<Film {}>'.format(self.title)


class User(db.Model):
    username = db.Column(db.String(128), primary_key=True)
    logged_films = db.Column(db.PickleType)
    num_pages = db.Column(db.Integer)
    avatar_url = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)