from flask import render_template, flash, redirect, session, url_for, jsonify
from app import app
from app.forms import LoginForm
from app.manager import update_db_with_new_films, get_user_films
from app.scraping import get_page_count, get_user_avatar_src
from app.director import *
import asyncio
import time
import urllib
from app.user import User

# test for loading screen
def convert(input):
    # Converts unicode to string
    if isinstance(input, dict):
        return {convert(key): convert(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [convert(element) for element in input]
    elif isinstance(input, str):
        return input.encode('utf-8')
    else:
        return input

'''
Trying out loading screen stuff. Change url_for to 'stats' to get the recently working thing.
'''
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        session['username'] = username
        return redirect(url_for('stats'))
    else:
        return render_template('login.html', title='Load data', form=form)


@app.route('/stats', methods=['GET'])
def stats():
    title = "Stats"
    username = session['username']
    num_pages = get_page_count(username)
    avatar_url = get_user_avatar_src(username)
    if num_pages == -1:
        flash('No user found. Try another username.')
        return redirect(url_for('login'))

    return render_template('stats.html', title=title, num_pages=num_pages, username=username, avatar_url=avatar_url)


@app.route('/directors', methods=["GET"])
def directors():

    async def inner():
        username = session['username']
        current_user = User(username)
        user_films = await get_user_films(current_user.username)
        current_user.logged_films = user_films
        await update_db_with_new_films(current_user.logged_films)
        top_directors = current_user.get_top_directors()
        return top_directors

    asyncio.set_event_loop(asyncio.SelectorEventLoop())
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(inner())
    top_directors = loop.run_until_complete(future)

    '''
    async def inner():
        username = session['username']
        num_pages = get_page_count(username)
        film_objects = await get_user_films(username)
        await update_db_with_new_films(film_objects)

        director_dict = generate_director_dictionary(film_objects)
        sorted_directors = sort_directors_by_biased_rating(director_dict.copy())
        top_directors_list = get_list_of_top_directors(sorted_directors, 150)
        return top_directors_list

    asyncio.set_event_loop(asyncio.SelectorEventLoop())
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(inner())
    top_directors_list = loop.run_until_complete(future)
    '''

    return jsonify(top_directors)


@app.route('/test/<text>', methods=['GET'])
def test(text):
    return render_template('test.html', text=text)
