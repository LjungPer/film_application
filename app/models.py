from app import db

director_film = db.Table('director_film',
                         db.Column('letterboxd_id', db.Integer, db.ForeignKey('film.letterboxd_id')),
                         db.Column('director_id', db.Integer, db.ForeignKey('director.director_id')))


class Director(db.Model):
    director_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    def __repr__(self):
        return '<Director {}>'.format(self.name)


class Film(db.Model):
    letterboxd_id = db.Column(db.Integer, primary_key=True)
    tmdb_id = db.Column(db.Integer, index=True, unique=True)
    title = db.Column(db.String(128))
    director = db.relationship('Director', secondary=director_film, backref=db.backref('films', lazy='dynamic'))

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
