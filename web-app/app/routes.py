from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Text
from app.forms import RegistrationForm, LoginForm, SubmitText, SearchText
from app import app, db
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from werkzeug.urls import url_parse
import time

@app.route('/time')
def get_current_time():
    data = {'time': time.time()}
    return jsonify(data)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    user = {'name': 'Mateusz', 'surname': 'Baryla'}
    submit_text_form = SubmitText()
    search_text_form = SearchText()

    if submit_text_form.validate_on_submit():
        category = dict(submit_text_form.categories.choices).get(submit_text_form.categories.data)
        text = Text(user_id=current_user.get_id(), title='first stance', characters=len(submit_text_form.text.data),
                    body=submit_text_form.text.data, category = category)
        text.mark_stance(submit_text_form.text.data)
        if text.stance == "TOO SHORT":
            submit_text_form.text.render_kw = {'style': "border: 1px solid blue;"}
            flash('Text is too short (<30 chars)!Sorry', "submit")
        elif text.stance == "NONE":
            submit_text_form.text.render_kw={'style': "border: 1px solid blue;"}
            flash('Cannot find stance in text! Sorry!',"submit")
        else:
            db.session.add(text)
            db.session.commit()
            flash('Successfully added text! Thanks!',"submit")
            submit_text_form.text.render_kw={'style': "border: 1px solid blue;"}
    if search_text_form.validate_on_submit():
        chosen_cat = (dict(search_text_form.categories.choices)[search_text_form.categories.data])
        chosen_data_from = search_text_form.date_from
        chosen_data_to = search_text_form.date_to
        texts_all = Text.query.all()
        texts_without_dates = Text.query.filter(Text.category == chosen_cat).all()
        texts_with_dates = Text.query.filter(Text.category == chosen_cat, Text.publication_date > chosen_data_from.data).all()
        if texts_with_dates != []:
            texts = texts_with_dates
            flash("Here are stances for chosen category and dates", "search")
            return render_template('index.html', user=user, submit_text_form=submit_text_form,
                               search_text_form=search_text_form, texts = texts)
        if texts_without_dates != []:
            texts = []
            flash("Nothing  found for these dates... Try with different date range?","search")
            return render_template('index.html', user=user, submit_text_form=submit_text_form,
                                   search_text_form=search_text_form, texts=texts)
        if texts_all != []:
            texts = []
            flash("Nothing  found for this tag and given date range... Try with similar tags?","search")
            return render_template('index.html', user=user, submit_text_form=submit_text_form,
                                   search_text_form=search_text_form, texts=texts)
    return render_template('index.html', user=user, submit_text_form=submit_text_form, search_text_form = search_text_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    login_form = LoginForm()
    register_form = RegistrationForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.username.data).first()
        if user is None or not user.check_password(login_form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=login_form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', login_form=login_form, register_form=register_form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    register_form = RegistrationForm()
    if register_form.validate_on_submit():
        user = User(username=register_form.username.data, email=register_form.email.data)
        user.set_password(register_form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', register_form=register_form)