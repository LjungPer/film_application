# Letterboxd-watched-film-statistics
A project started and developed for the purpose of computing fun, yet rigorous, statistics on people's logged film watching data. In addition, it has been used to practice the ability of structuring larger programming projects (not limited to single scripts) in an organized way, by following guidelines of clean coding. 

## Overview of application
A website that analyses your film watching statistics based on your Letterboxd user data. The project lets the user enter any user's username from the film based social media site [Letterboxd](www.letterboxd.com), and computes interesting statistics from logged films. Examples of such include, yet not limited to:
* Favorite directors, actors/actresses, year of release, genres, spoken languages, etc., where favorite can be alternated between measures such as average rating, number of films watched, or a biased type rating that takes both former measures into account.
* The user's "diary data". How many films did the user watch back in 2020? How many films does the user watch depending on what month it is (and is it a lower amount during summer in comparison to winter)? How many times have the user seen a certain films? And many more such questions.
* List completions. Have you seen all films on [IMDb Top 250](https://www.imdb.com/chart/top/), and if not, how many films remain? What more interesting lists are you looking to complete, and what films should you watch next for this purpose?

## Implementation
The project is implemented using Python 3.8.x along with the [Flask](https://flask.palletsprojects.com/en/2.2.x/) package for web development.
