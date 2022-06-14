from flask import render_template, flash, redirect, session, url_for, jsonify
from app import app
from app.forms import LoginForm, UpdateDataForm
from app.manager import update_db_with_new_films, set_up_user, update_user
from app.director import *
import asyncio
from app.user import get_top_directors


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
        print("test")
        return redirect(url_for('loading'))

    return render_template('tmp_stats.html', num_pages=num_pages, username=username, avatar_url=avatar_url, form=form)


@app.route('/directors', methods=["GET"])
def directors():

    username = session['username']
    top_directors = get_top_directors(username)

    return jsonify(top_directors)


@app.route('/loading', methods=['GET'])
def loading():
    return render_template('loading.html')


@app.route('/update_data', methods=['GET', 'POST'])
def update_data():

    username = session['username']
    update_user(username)

    return redirect(url_for('stats'))
