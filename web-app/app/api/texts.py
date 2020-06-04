from app.api import bp
from flask import jsonify
from app.models import Text,User, TextCategory
from flask import request
from app.api.errors import bad_request
from flask import url_for
from app import db
from flask import g, abort
from app.api.auth import token_auth
from sqlalchemy import func
import pandas as pd
import fasttext
import os
import string
from nltk import FreqDist

@bp.route('/texts/common', methods=['GET'])
def get_most_common_words():
    texts = Text.query.with_entities(Text.body).all()
    texts = [text[0] for text in texts]
    word_dict = {}
    for tweet in texts:
        tweet_tokn = tweet.split(" ")
        for word in tweet_tokn:
            if len(word) == 1:
                break
            if len(word) >1 and (word[0] == "#" or word[0] == "@"):
                break
            if word == "":
                break
            if word in word_dict:
                word_dict[word] +=1
            else:
                word_dict[word] = 1
    word_dict = dict(sorted(word_dict.items(), key=lambda x: x[1])[-25:][::-1])
    allvals = []
    for word,value in word_dict.items():
        new_dic = {}
        new_dic['label'] = word
        new_dic['value'] = value
        allvals.append(new_dic)

    return jsonify({'wordData':allvals})

@bp.route('/texts/hist', methods=['GET'])
def get_letters_hist():
    texts = Text.query.with_entities(Text.body).all()
    letters_hist = [text[0] for text in texts]
    snt_dict = {}
    for sentence in letters_hist:
        for letter in sentence.lower():
            if letter in string.ascii_letters:
                if letter in snt_dict:
                    snt_dict[letter] +=1
                else:
                    snt_dict[letter] = 1
    allvals = []
    for key, val in snt_dict.items():
        new_dic = {}
        new_dic['label'] = key
        new_dic['value'] = val
        allvals.append(new_dic)

    return jsonify({'lettersData':allvals})

@bp.route('/texts/<int:qnt>', methods=['GET'])
def get_texts(qnt):
    # headers = request.headers['your-header-name']
    # print('setting current user to barry')
    # user = User.query.filter_by(username='barry').first()
    # g.current_user = user
    # if not token_auth.verify_token(headers['token']):
    #     return #authentication token is bad
    texts = Text.query.limit(qnt)
    texts_dict = [text.to_dict() for text in texts]
    return jsonify(texts_dict)

@bp.route('/texts/<string:sortable>/<string:how>', methods=['GET'])
def sort_texts(sortable,how):
    # headers = request.headers['your-header-name']
    # print('setting current user to barry')
    # user = User.query.filter_by(username='barry').first()
    # g.current_user = user
    # if not token_auth.verify_token(headers['token']):
    #     return #authentication token is bad
    srt_dict = {'id':Text.id,
                'tweet':Text.body,
                'date':Text.publication_date,
                'stance':Text.stance,
                'opinion': Text.opinion_towards,
                'sentiment': Text.sentiment,
                'target': Text.target}
    if how == "up":
        texts = Text.query.order_by(srt_dict[sortable].asc()).limit(5)
    elif how == "down":
        texts = Text.query.order_by(srt_dict[sortable].desc()).limit(5)
    elif how == "default":
        texts = Text.query.order_by(srt_dict[sortable]).limit(5)
    texts_dict = [text.to_dict() for text in texts]
    return jsonify(texts_dict)

@bp.route('/texts/grouped', methods=['GET'])
def get_grouped_text():
    # headers = request.headers['your-header-name']
    # print('setting current user to barry')
    # user = User.query.filter_by(username='barry').first()
    # g.current_user = user
    # if not token_auth.verify_token(headers['token']):
    #     return #authentication token is bad
    df_march = pd.read_sql(db.session.query(Text)\
                     .filter(func.extract('month',Text.publication_date)==3)\
                     .statement,db.session.bind)
    df_march["day"] = df_march["publication_date"].dt.day
    values_march = df_march.groupby('day').count()["body"].values.tolist()

    df_april = pd.read_sql(db.session.query(Text) \
                           .filter(func.extract('month', Text.publication_date) == 4) \
                           .statement, db.session.bind)
    df_april["day"] = df_april["publication_date"].dt.day
    values_april = df_april.groupby('day').count()["body"].values.tolist()

    return jsonify({'previousMonthData': values_march,\
                   'currentMonthData': values_april})

@bp.route('/texts/count/<string:attribute>', methods=['GET'])
def count_texts(attribute):
    # headers = request.headers['your-header-name']
    # print('setting current user to barry')
    # user = User.query.filter_by(username='barry').first()
    # g.current_user = user
    # if not token_auth.verify_token(headers['token']):
    #     return #authentication token is bad
    unq_targets = ["Atheism", "Climate Change is a Real Concern",
                   "Feminist Movement", 'Hillary Clinton',
                   'Legalization of Abortion']
    texts_dict = []
    grp_dict = {'stance':Text.stance,\
                'sentiment':Text.sentiment,\
                'opinion':Text.opinion_towards}
    for trgt in unq_targets:
        new_dic = {}
        texts = db.session.query(
            Text.stance,
            func.count(Text.stance)).filter(Text.target==trgt).group_by(grp_dict[attribute]).order_by(Text.stance).all()
        print(texts)
        new_dic['target'] = trgt
        new_dic['value'] = [text[1] for text in texts]
        texts_dict.append(new_dic)
    print(texts_dict)
    return jsonify(texts_dict)

@bp.route('/texts', methods=['POST'])
def add_text():
    data = request.get_json() or {}
    user = User.query.filter_by(email='230038@student.pwr.edu.pl').first()
    g.current_user = user
    if not token_auth.verify_token(data['token']):
        print('token not verified')
        return #authentication token is bad
    if 'body' not in data:
        return bad_request('Please specify text body and try again.')
    if len(data['body']) <10:
        return bad_request('Text is too short try again.')
    # if Text.query.filter_by(body=data['body']).first():
    #     return bad_request('This text has already been marked.')
    text = Text(user_id = g.current_user.id, body = data['body'])
    text.from_dict(data)
    db.session.add(text)
    db.session.flush()
    db.session.commit()
    model_target = fasttext.load_model("..\\stance-tagger-kedro\\data\\06_models\\model_classification.bin")
    model_prediction = model_target.predict(data["body"])[0][0]
    print(model_prediction)
    stances_dict = {'__label__legalization_of_abortion':'Legalization of Abortion',
                     '__label__hillary_clinton':"Hillary Clinton",
                     '__label__feminist_movement':"Feminist Movement",
                     '__label__atheism':"Atheism",
                     '__label__climate_change_is_a_real_concern':"Climate Change is a Real Concern"}
    text.target = stances_dict[model_prediction]
    ############################################
    model_target = fasttext.load_model("..\\stance-tagger-kedro\\data\\06_models\\model_favour_against.bin")
    model_prediction = model_target.predict(data["body"])[0][0]
    favour_against_dict = {'__label__favour': 'FAVOUR',
                           '__label__none': "NONE",
                           '__label__against': "AGAINST"}
    text.stance = favour_against_dict [model_prediction]
    ############################################
    model_target = fasttext.load_model("..\\stance-tagger-kedro\\data\\06_models\\model_opinion_towards.bin")
    model_prediction = model_target.predict(data["body"])[0][0]
    favour_against_dict = {'__label__target': 'TARGET',
                           '__label__other': "OTHER",
                           '__label__noone': "NO ONE"}
    text.opinion_towards = favour_against_dict[model_prediction]
    ############################################
    model_target = fasttext.load_model("..\\stance-tagger-kedro\\data\\06_models\\model_sentiment.bin")
    model_prediction = model_target.predict(data["body"])[0][0]
    sentiment_dict = {'__label__positive': 'POSITIVE',
                       '__label__negative': "NEGATIVE",
                       '__label__neither': "NEITHER"}
    text.sentiment = sentiment_dict[model_prediction]


    response = jsonify(text.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.add_text', id=text.id)
    return response