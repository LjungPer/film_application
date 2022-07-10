from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('Letterboxd username', validators=[DataRequired()])
    submit = SubmitField('Load data')


class UpdateDataForm(FlaskForm):
    submit = SubmitField('Update data')


class FetchYearDataForm(FlaskForm):
    year = StringField('Search year', validators=[DataRequired()])
    submit = SubmitField('Check')
