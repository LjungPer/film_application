from audioop import avg
import json
from flask import render_template, flash, redirect, session, url_for, jsonify
from app import app
from app.forms import LoginForm, UpdateDataForm, FetchYearDataForm, ReusableForm
from app.manager import get_data_for_all_directors, update_db_with_new_films, set_up_user, update_user_info, get_ratings_from_films, get_data_for_all_years
from app.user import update_user_statistics
from app.fetch import get_top_category
from app.database import query_user_films_from_year, query_user_years, query_user


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        session['username'] = username
        set_up_user(username)
        u = query_user(username)
        session['pages'] = u.pages
        session['avatar_url'] = u.avatar_url

        return redirect(url_for('stats'))
    else:
        return render_template('login.html', title='Load data', form=form)


@app.route('/stats', methods=['GET', 'POST'])
def stats():
    update_data_form = UpdateDataForm()

    if session['pages'] == -1:
        session.pop('username', None)
        session.pop('pages', None)
        flash('No user found. Try another username.')
        return redirect(url_for('login'))

    if update_data_form.validate_on_submit():
        return redirect(url_for('loading'))

    return render_template('stats.html', form=update_data_form)


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


@app.route('/years', methods=['GET', 'POST'])
def years():
    username = session['username']
    all_years, avg, bias, nr_films = get_data_for_all_years(username)
    year_form = ReusableForm()
    # options should be str so that empty choice option is valid
    possible_names = query_user_years(username)
    year_form.name.choices = [("", "")] + [(uuid, name)
                                           for uuid, name in possible_names.items()]

    if year_form.validate_on_submit() and year_form.name.data:
        year = year_form.name.data
        return redirect(url_for('year', year=year))

    return render_template('years.html', years=all_years, avg=avg, bias=bias, 
                            nr_films=nr_films, year_form=year_form,
                            most_films=all_years[nr_films.index(max(nr_films))], 
                            avg_year=all_years[avg.index(max(avg))])


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


@app.route('/directors', methods=['GET', 'POST'])
def directors():
    username = session['username']
    avg, bias, nr_films = get_data_for_all_directors(username)
    year_form = ReusableForm()
    # options should be str so that empty choice option is valid
    possible_names = query_user_years(username)
    year_form.name.choices = [("", "")] + [(uuid, name)
                                           for uuid, name in possible_names.items()]

    if year_form.validate_on_submit() and year_form.name.data:
        year = year_form.name.data
        return redirect(url_for('year', year=year))

    avg_labels = [tmp[1] for tmp in avg]
    avg_scores = [tmp[2] for tmp in avg]
    bias_labels = [tmp[1] for tmp in bias]
    bias_scores = [tmp[3] for tmp in bias]
    nr_films_labels = [tmp[1] for tmp in nr_films]
    nr_films_scores = [tmp[4] for tmp in nr_films]
    return render_template('directors.html', avg=avg_scores, avg_labels=avg_labels, bias=bias_scores, bias_labels=bias_labels, 
                            nr_films=nr_films_scores, nr_films_labels=nr_films_labels, year_form=year_form)

    #return render_template('directors.html', year_form=year_form)