from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Required, Length
from app.models import User
from wtforms.fields.html5 import DateField
import datetime

class SearchText(FlaskForm):
    date_from = DateField('Date from', format='%Y-%m-%d', default=datetime.datetime.today()-datetime.timedelta(days=7))
    date_to = DateField('Date to', format='%Y-%m-%d', default=datetime.datetime.today())
    categories = SelectField(u'Field name', choices=[('0', 'Atheism'), ('1', 'Climate Change is a Real Concern'), \
                                                     ('2', 'Feminist Movement'), ('3', 'Hillary Clinton'),
                                                     ('4', 'Legalization of Abortion'),
                                                     ('5', 'Euthanasia')])
    submit = SubmitField('Search')

class SubmitText(FlaskForm):
    added_text = "#Clintonemails are just a prelude of what her presidency could be if elected, a myrad of scandals @GOP @FloridaGOP @marcorubio #SemST"
    added_text = ""
    def_title = "OKK"
    def_title = ""
    text = TextAreaField('Stance', [Length( max=2000)], default=added_text)
    title = StringField('Title', [Length(max=50)], default=def_title)
    categories = SelectField(u'Field name', choices=[('0', 'Atheism'), ('1', 'Climate Change is a Real Concern'), \
                                                     ('2', 'Feminist Movement'), ('3', 'Hillary Clinton'),
                                                     ('4', 'Legalization of Abortion'),
                                                     ('5', 'Euthanasia')])
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me', default="checked")
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Sign up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')