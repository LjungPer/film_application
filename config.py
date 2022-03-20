import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess??'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')   # Configure from environment variable, else create app.db
    SQLALCHEMY_TRACK_MODIFICATIONS = False              # Don't signal the app when change in db is about to happen
