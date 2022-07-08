from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import tmdbsimple as tmdb
from flask_jsglue import JSGlue

app = Flask(__name__)
jsglue = JSGlue(app)
app.config.from_object(Config)
db = SQLAlchemy(app)    # Represents the database
migrate = Migrate(app, db)  # Migration engine
tmdb.API_KEY = '91ec5247331918ba61bd79baa377e4d2'

# Models define the structure of the database
from app import routes, models