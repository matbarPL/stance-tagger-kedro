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

@bp.route('/texts/count', methods=['GET'])
def count_texts():
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
    for trgt in unq_targets:
        new_dic = {}
        texts = db.session.query(
            Text.stance,
            func.count(Text.stance)).filter(Text.target==trgt).group_by(Text.stance).order_by(Text.stance).all()
        print(texts)
        new_dic['target'] = trgt
        new_dic['value'] = [text[1] for text in texts]
        texts_dict.append(new_dic)
    print(texts_dict)
    return jsonify(texts_dict)

@bp.route('/texts', methods=['POST'])
def add_text():
    data = request.get_json() or {}
    print('setting current user to barry')
    user = User.query.filter_by(username='barry').first()
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
    text = Text(user_id = g.current_user.id, body = data['body'], target=data['category'])
    text.from_dict(data)
    db.session.add(text)
    db.session.flush()
    db.session.commit()
    print(data['category'])
    if data['category'] == "Unspecified":
        model_target = fasttext.load_model("..\\stance-tagger-kedro\\data\\06_models\\model_classification.bin")
        model_prediction = model_target.predict("body")[0][0]
        stances_dict = {'__label__legalization_of_abortion':'Legalization of Abortion',
                         '__label__hillary_clinton':"Hillary Clinton",
                         '__label__feminist_movement':"Feminist Movement",
                         '__label__atheism':"Atheism",
                         '__label__climate_change_is_a_real_concern':"Climate Change is a Real Concern"}
        text.target = stances_dict[model_prediction]
        ############################################
        model_target = fasttext.load_model("..\\stance-tagger-kedro\\data\\06_models\\model_favour_against.bin")
        model_prediction = model_target.predict("body")[0][0]
        favour_against_dict = {'__label__favour': 'FAVOUR',
                        '__label__against': "AGAINST"}
        text.stance = favour_against_dict [model_prediction]


    response = jsonify(text.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.add_text', id=text.id)
    return response