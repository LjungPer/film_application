from flask import render_template, flash, redirect, session, url_for, render_template_string
from app import app
from app.forms import LoginForm
#from flask_login import current_user, login_user
from app.database import update_database
from app.scraping import get_page_count, get_user_ratings
from app.director import *
import asyncio
import time
import urllib

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

@app.route('/loading/<text>', methods=['GET'])
def loading(text):
    some_data = "Here's some example data"
    some_data = urllib.parse.quote(convert(some_data))
    return render_template('loading.html', text=text)


@app.route('/user_data', methods=['GET', 'POST'])
def user_data():
    print(session)
    username = session['username']
    num_pages = get_page_count(username)
    session['num_pages'] = num_pages
    if num_pages == -1:
        flash('No user found. Try another username.')
        return redirect(url_for('login'))

    start = time.time()
    asyncio.set_event_loop(asyncio.SelectorEventLoop())
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(get_user_ratings(username, num_pages))
    film_objects = loop.run_until_complete(future)
    session['film_objects'] = film_objects # dumt dåligt
    end = time.time()
    print('Time to construct film_objects is {time}'.format(time=end - start))
    return redirect(url_for('loading', text='update_db'))


@app.route('/processing/<text>', methods=['GET'])
def processing(text):
    print(session)
    title = "Stats"
    username = session['username']
    num_pages = session['num_pages']
    film_objects = session['film_objects']
    print(len(film_objects))
    return render_template('test.html', text=text)

    '''
    if num_pages == -1:
        flash('No user found. Try another username.')
        return redirect(url_for('login'))
    else:
        if text == 'user_data':
            start = time.time()
            asyncio.set_event_loop(asyncio.SelectorEventLoop())
            loop = asyncio.get_event_loop()
            future = asyncio.ensure_future(get_user_ratings(username, num_pages))
            film_objects = loop.run_until_complete(future)
            session['film_objects'] = film_objects
            print(len(film_objects))
            print(len(session['film_objects']))
            end = time.time()
            print('Time to construct film_objects is {time}'.format(time=end - start))
            return redirect(url_for('loading', text='update_db'))

        elif text == 'update_db':
            print('wehere')
            print(len(session['film_objects']))
            start = time.time()
            loop = asyncio.get_event_loop()
            future = asyncio.ensure_future(update_database(session['film_objects']))
            loop.run_until_complete(future)
            end = time.time()
            print('Time to update database is {time}'.format(time=end - start))
            return redirect(url_for('loading', text='generate_dir'))

        elif text == 'generate_dir':
            start = time.time()
            director_dict = generate_director_dictionary(session['film_objects'])
            sorted_directors = sort_directors_by_biased_rating(director_dict.copy())
            top_directors_list = get_list_of_top_directors(sorted_directors, 150)
            end = time.time()
            print('Time to generate and sort directors is {time}'.format(time=end - start))
            return render_template('stats.html', title=title, num_pages=num_pages, username=username,
                                       top_directors_list=top_directors_list)

        else:
            return render_template('test.html', text=text)
            '''

@app.route('/stats', methods=['GET'])
def stats():
    title = "Stats"
    username = session['username']
    num_pages = get_page_count(username)
    if num_pages == -1:
        flash('No user found. Try another username.')
        return redirect(url_for('login'))
    else:
        start = time.time()
        asyncio.set_event_loop(asyncio.SelectorEventLoop())
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(get_user_ratings(username, num_pages))
        film_objects = loop.run_until_complete(future)
        end = time.time()
        print('Time to construct film_objects is {time}'.format(time=end-start))
        flash('User {username} has logged {no_films} films'.format(username=username, no_films=len(film_objects)))

        start = time.time()
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(update_database(film_objects))
        loop.run_until_complete(future)
        end = time.time()
        print('Time to update database is {time}'.format(time=end-start))

        start = time.time()
        director_dict = generate_director_dictionary(film_objects)
        sorted_directors = sort_directors_by_biased_rating(director_dict.copy())
        top_directors_list = get_list_of_top_directors(sorted_directors, 150)
        end = time.time()
        print('Time to generate and sort directors is {time}'.format(time=end-start))

    return render_template('stats.html', title=title, num_pages=num_pages, username=username,
                           top_directors_list=top_directors_list)


@app.route('/test/<text>', methods=['GET'])
def test(text):
    return render_template('test.html', text=text)
