# Letterboxd-watched-film-statistics
A project started and developed for the purpose of computing fun, yet rigorous, statistics on people's logged film watching data. In addition, it has been used to practice the ability of structuring larger programming projects (not limited to single scripts) in an organized way, by following guidelines of clean coding. The website is currently not deployed, but a demo is provided [further down](#demo).

## Overview of application
A website that analyses your film watching statistics based on your Letterboxd user data. The project lets the user enter any user's username from the film based social media site [Letterboxd](www.letterboxd.com), and computes interesting statistics from logged films. Examples of such include, yet not limited to:
* Favorite directors, actors/actresses, year of release, genres, spoken languages, etc., where favorite can be alternated between measures such as average rating, number of films watched, or a biased type rating that takes both former measures into account.
* The user's "diary data". How many films did the user watch back in 2020? How many films does the user watch depending on what month it is (and is it a lower amount during summer in comparison to winter)? How many times have the user seen a certain films? And many more such questions.
* List completions. Have you seen all films on [IMDb Top 250](https://www.imdb.com/chart/top/), and if not, how many films remain? What more interesting lists are you looking to complete, and what films should you watch next for this purpose?

## Implementation
The project is implemented using Python 3.8.x along with the [Flask](https://flask.palletsprojects.com/en/2.2.x/) package for web development. Examples of technical aspects, packages etc., that has been used, and for what purpose, include:
* `Web scraping:` for collection of user data. Mainly implemented using the [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) package.
* `Asynchronous programming:` to speed up scraping. Performed using the [asyncio](https://docs.python.org/3/library/asyncio.html) module.
* `Data collecting:` information on films (titles, crew members, etc.) collected using the [TMDb](www.tmdb.com) API.
* `Databases`: done using the ORM [SQLAlchemy](https://www.sqlalchemy.org/) via the flask extension [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/).
* `Web desgin:` basics done with HTML, with design choices using JavaScript and CSS.


## Demo

Below follows a demo of the website's current state.

#### Login user
Possbility to enter any user's username, such that both your own and your friends data can be analysed.
<p align="center">
<img src="https://github.com/LjungPer/film_application/blob/main/demo_figures/login.jpg" data-canonical-src="https://github.com/LjungPer/film_application/blob/main/demo_figures/login.jpg" width="511" height="248" />
 </p>
 
 #### First time username is entered
 Before an analysis can be made of the user's watched films, the user is prompted to update the data.
 <p align="center">
<img src="https://github.com/LjungPer/film_application/blob/main/demo_figures/kattihatt2.jpg" data-canonical-src="https://github.com/LjungPer/film_application/blob/main/demo_figures/kattihatt2.jpg" width="766" height="364" />
 </p>

#### When data up to date
A navigation bar appear at top of the page where the user may choose what type of statistics they wish to check out.
 <p align="center">
<img src="https://github.com/LjungPer/film_application/blob/main/demo_figures/navbar.jpg" data-canonical-src="https://github.com/LjungPer/film_application/blob/main/demo_figures/navbar.jpg" width="607" height="67" />
 </p>
 
 #### Example: Data from films by release year
 
 <p align="left">
  <img src="https://github.com/LjungPer/film_application/blob/main/demo_figures/average_year.jpg" data-canonical-src="https://github.com/LjungPer    /film_application/blob/main/demo_figures/average_year.jpg" width="365" height="222" />
</p>
 
<p align="center">
 <img src="https://github.com/LjungPer/film_application/blob/main/demo_figures/bias_rating_per_year.jpg" data-canonical-src="https://github.com/LjungPer/film_application/blob/main/demo_figures/bias_rating_per_year.jpg" width="365" height="222" />
</p>

<p align="right">
 <img src="https://github.com/LjungPer/film_application/blob/main/demo_figures/number_of_films_per_year.jpg" data-canonical-src="https://github.com/LjungPer/film_application/blob/main/demo_figures/number_of_films_per_year.jpg" width="365" height="222" />
</p>
