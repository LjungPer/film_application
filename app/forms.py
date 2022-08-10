from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, InputRequired


class LoginForm(FlaskForm):
    username = StringField('Letterboxd username', validators=[DataRequired()])
    submit = SubmitField('Load data')


class UpdateDataForm(FlaskForm):
    submit = SubmitField('Update data')


class FetchYearDataForm(FlaskForm):
    submit = SubmitField('Year data')


class YearSearchForm(FlaskForm):
    name = SelectField("Enter year",
                        render_kw={'style': 'width: 150px'},
                        validators=[DataRequired()])
    submit = SubmitField('Search')


class NameSearchForm(FlaskForm):
    name = SelectField("Enter name",
                        render_kw={'style': 'width: 150px'},
                        validators=[DataRequired()])
    submit = SubmitField('Search')