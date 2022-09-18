from flask import render_template, flash, redirect, session, url_for, jsonify
from app import app
from app.diary import get_diary_info
from app.forms import LoginForm, UpdateDataForm, YearSearchForm, NameSearchForm
from app.manager import (
    extract_yearly_diary_data,
    get_basic_data_from_year,
    get_data_for_all_of_category, 
    get_data_for_all_years,
    get_ratings_from_films,
    update_db_with_new_films,
    update_user_info,
    set_up_user,
    get_diary_info_from_year,
    update_user_diary
)
from app.user import update_user_statistics
from app.fetch import get_top_category
from app.database import (
    query_category_search_labels,
    query_user,
    query_user_films_from_member,
    query_user_films_from_year,
    query_user_member_from_category,
    query_user_years,
    query_user_attr
) 


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
        if query_user_attr(username, 'Year') is None:
            session['updated'] = False
        else:
            session['updated'] = True

        return redirect(url_for('home'))
    else:
        return render_template('login.html', title='Load data', form=form)


@app.route('/home', methods=['GET', 'POST'])
def home():
    update_data_form = UpdateDataForm()

    if session['pages'] == -1:
        session.pop('username', None)
        session.pop('pages', None)
        flash('No user found. Try another username.')
        return redirect(url_for('login'))

    if update_data_form.validate_on_submit():
        return redirect(url_for('loading'))

    return render_template('home.html', form=update_data_form)


@app.route('/categories/<category_type>/<sorting_type>', methods=["GET"])
def categories(category_type, sorting_type):

    username = session['username']
    top_category_biased = get_top_category(username, str(
        category_type), sorting_type=str(sorting_type))
    return jsonify(top_category_biased)


@app.route('/loading', methods=['GET'])
def loading():
    return render_template('loading.html')

@app.route('/loading_diary', methods=['GET'])
def loading_diary():
    return render_template('loading_diary.html')

@app.route('/update_data', methods=['GET', 'POST'])
def update_data():

    username = session['username']
    user_films = update_user_info(username, return_logged_films=True)
    update_db_with_new_films(user_films)
    update_user_statistics(username)
    session['updated'] = True

    return redirect(url_for('home'))


@app.route('/years', methods=['GET', 'POST'])
def years():
    username = session['username']
    all_years, avg, bias, nr_films = get_data_for_all_years(username)
    year_form = YearSearchForm()
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


@app.route('/years/<year>', methods=['GET', 'POST'])
def year(year):
    username = session['username']
    year_form = YearSearchForm()
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


@app.route('/category/<category>', methods=['GET', 'POST'])
def stats(category):
    username = session['username']
    avg, bias, nr_films = get_data_for_all_of_category(username, category)
    category_form = NameSearchForm()
    # options should be str so that empty choice option is valid
    possible_names = query_category_search_labels(username, category)
    category_form.name.choices = [("", "")] + [(uuid, name)
                                           for uuid, name in possible_names.items()]

    if category_form.validate_on_submit() and category_form.name.data:
        category_id = category_form.name.data
        return redirect(url_for('stat', category=category, id=category_id))

    avg_labels = [tmp[1] for tmp in avg]
    avg_scores = [tmp[2] for tmp in avg]
    bias_labels = [tmp[1] for tmp in bias]
    bias_scores = [tmp[3] for tmp in bias]
    nr_films_labels = [tmp[1] for tmp in nr_films]
    nr_films_scores = [tmp[4] for tmp in nr_films]
    return render_template('stats.html',
                            avg=[avg_scores, avg_labels],
                            bias=[bias_scores, bias_labels], 
                            nr_films=[nr_films_scores, nr_films_labels],
                            category_form=category_form,
                            category_type=category.capitalize())

                        
@app.route('/category/<category>/<id>', methods=['GET', 'POST'])
def stat(category, id):
    username = session['username']
    member = query_user_member_from_category(username, category, id)
    member_form = NameSearchForm()
    possible_names = query_category_search_labels(username, category)
    member_form.name.choices = [("", "")] + [(uuid, name)
                                           for uuid, name in possible_names.items()]
    user_films_from_member = query_user_films_from_member(
        username, category, id, sort=True)
    ratings, _ = get_ratings_from_films(user_films_from_member)

    if member_form.validate_on_submit() and member_form.name.data:
        member_id = member_form.name.data
        return redirect(url_for(category, id=member_id))

    return render_template('stat.html', 
                            category=member, 
                            category_form=member_form, 
                            films=user_films_from_member, 
                            label=list(range(1, 11)), 
                            data=ratings, 
                            category_type=category)


@app.route('/diary', methods=['GET', 'POST'])
def diary():
    username = session['username']
    diary = query_user_attr(username, 'Diary')
    if ('diary_entries' not in session or diary is None or session['diary_entries'] != len(diary)):
        update_user_diary(username)
        session['diary_entries'] = len(query_user_attr(username, 'Diary'))
        diary = query_user_attr(username, 'Diary')
    
    yearly_diary = extract_yearly_diary_data(diary)
    year_form = YearSearchForm()
    year_form.name.choices = [("", "")] + [(year, year) for year in list(yearly_diary.keys())] 

    if year_form.validate_on_submit() and year_form.name.data:
        year = year_form.name.data
        return redirect(url_for('diary_year', year=year))

    return render_template('diary.html', year_form=year_form)


@app.route('/diary/<year>', methods=['GET', 'POST'])
def diary_year(year):
    year = int(year)
    username = session['username']
    watch_data = get_diary_info(username, year, 'Watch')
    time_data = get_diary_info(username, year, 'Time')
    top_data = get_diary_info(username, year, 'Top')

    return render_template('diary_year.html', 
                            year=year, 
                            watch_data=watch_data,
                            time_data=time_data,
                            top_data=top_data)