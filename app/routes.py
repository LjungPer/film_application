from flask import render_template, flash, redirect, session, url_for, jsonify
from app import app
from app.forms import LoginForm, UpdateDataForm, FetchYearDataForm
from app.manager import update_db_with_new_films, set_up_user, update_user_info
from app.user import update_user_statistics
from app.fetch import get_top_category
from app.models import User


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
    year_form = FetchYearDataForm()
    username = session['username']
    u = User.query.get(username)
    pages = u.pages
    avatar_url = u.avatar_url
    if pages == -1:
        flash('No user found. Try another username.')
        return redirect(url_for('login'))

    if year_form.validate_on_submit() and year_form.year.data:
        year = year_form.year.data
        session['year'] = year
        return redirect(url_for('year'))

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

@app.route('/year', methods=['GET'])
def year():
    year = session['year']
    return render_template('year.html', year=year)