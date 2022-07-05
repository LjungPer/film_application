from flask import render_template, flash, redirect, session, url_for, jsonify
from app import app
from app import user
from app.forms import LoginForm, UpdateDataForm
from app.manager import update_db_with_new_films, set_up_user, update_user_info
from app.user import get_top_directors_biased, update_user_statistics, get_top_countries_biased
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
    form = UpdateDataForm()
    username = session['username']
    u = User.query.get(username)
    num_pages = u.num_pages
    avatar_url = u.avatar_url
    if num_pages == -1:
        flash('No user found. Try another username.')
        return redirect(url_for('login'))

    if form.validate_on_submit():
        return redirect(url_for('loading'))

    return render_template('stats.html', num_pages=num_pages, username=username, avatar_url=avatar_url, form=form)


@app.route('/categories/<category_type>', methods=["GET"])
def categories(category_type):
    

    print(str(category_type) == 'Director')

    username = session['username']
    if str(category_type) == 'Director':
        return jsonify(get_top_directors_biased(username))
    if str(category_type) == 'Country':
        return jsonify(get_top_countries_biased(username))


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
