from audioop import avg
import json
from flask import render_template, flash, redirect, session, url_for, jsonify
from app import app
from app.forms import LoginForm, UpdateDataForm, FetchYearDataForm, ReusableForm
from app.manager import update_db_with_new_films, set_up_user, update_user_info, get_ratings_from_films
from app.user import update_user_statistics
from app.fetch import get_top_category
from app.models import User
from app.database import query_user_films_from_year, query_user_years


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        session['username'] = username
        set_up_user(username)
        return redirect(url_for('stats'))
    else:
        return render_template('login.html', title='Load data', form=form)


@app.route('/stats', methods=['GET', 'POST'])
def stats():
    update_data_form = UpdateDataForm()
    #year_form = FetchYearDataForm()
    year_form = ReusableForm()

    username = session['username']
    u = User.query.get(username)
    # options should be str so that empty choice option is valid
    possible_names = query_user_years(username)
    year_form.name.choices = [("", "")] + [(uuid, name)
                                           for uuid, name in possible_names.items()]
    pages = u.pages
    avatar_url = u.avatar_url
    if pages == -1:
        flash('No user found. Try another username.')
        return redirect(url_for('login'))

    if year_form.validate_on_submit() and year_form.name.data:
        year = year_form.name.data
        return redirect(url_for('year', year=year))

    # if year_form.validate_on_submit() and year_form.name.data:
    #    print(year_form.name.data)
    #    return redirect(url_for('stats'))

    if update_data_form.validate_on_submit():
        return redirect(url_for('loading'))

    return render_template('stats.html', num_pages=pages, username=username, avatar_url=avatar_url, form=update_data_form, year_form=year_form)


@app.route('/categories/<category_type>/<sorting_type>', methods=["GET"])
def categories(category_type, sorting_type):

    username = session['username']
    top_category_biased = get_top_category(username, str(
        category_type), sorting_type=str(sorting_type))
    return jsonify(top_category_biased)


@app.route('/loading', methods=['GET'])
def loading():
    return render_template('loading.html')


@app.route('/update_data', methods=['GET', 'POST'])
def update_data():

    username = session['username']
    user_films = update_user_info(username, return_logged_films=True)
    update_db_with_new_films(user_films)
    update_user_statistics(username)

    return redirect(url_for('stats'))


@app.route('/year/<year>', methods=['GET', 'POST'])
def year(year):
    username = session['username']
    year_form = ReusableForm()
    # options should be str so that empty choice option is valid
    possible_names = query_user_years(username)
    year_form.name.choices = [("", "")] + [(uuid, name)
                                           for uuid, name in possible_names.items()]
    user_films_from_year = query_user_films_from_year(
        username, year, sort=True)
    nr_films = len(user_films_from_year)
    ratings, avg_rating = get_ratings_from_films(user_films_from_year)

    if year_form.validate_on_submit() and year_form.name.data:
        year = year_form.name.data
        return redirect(url_for('year', year=year))

    return render_template('year.html', year=year, films=user_films_from_year,
                           label=list(range(1, 11)), data=ratings, nr_films=nr_films,
                           avg_rating=avg_rating, year_form=year_form)
