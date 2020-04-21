from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from flask import url_for
import base64
from datetime import datetime, timedelta
import os
from flask_jwt_extended import (create_access_token)
from flask import g

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data

class User(PaginatedAPIMixin, UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(64))
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True, index=True)
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def from_dict(self, data, new_user=False):
        for field in ['username', 'email']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    def to_dict(self, include_email=False):
        data = {
            'id': self.id,
            'username': self.username,
            'token': self.token,
            '_links': {
                'self': url_for('api.get_user', id=self.id)
            }
        }
        if include_email:
            data['email'] = self.email
        return data

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        # setattr(self, 'token', base64.b64encode(os.urandom(24)).decode('utf-8'))
        access_token = create_access_token(
            identity={'username': self.username, 'email': self.email})
        setattr(self, 'token', access_token)
        setattr(self,'token_expiration', now + timedelta(seconds=expires_in))
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Text(PaginatedAPIMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    publication_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.ForeignKey('user.id'))
    body = db.Column(db.String) #text put into form for submission
    title = db.Column(db.String, default ='') #title text put into form for submission
    stance = db.Column(db.String) #AGAINST, FAVOR,  NONE
    opinion_towards = db.Column(db.String) #OTHER, TARGET, NO ONE
    sentiment = db.Column(db.String) #POSITIVE,NEGATIVE
    target = db.Column(db.String) #Atheism Climate ...

    def to_dict(self):
        data = {
            'id': self.id,
            'publication_date': self.publication_date,
            'user_id': self.user_id,
            'body': self.body,
            'title': self.title,
            'stance': self.stance,
            'opinion_towards': self.opinion_towards,
            'sentiment': self.sentiment,
            'target': self.target
        }
        return data

    def from_dict(self, data):
        setattr(self, 'body', data['body'])
        setattr(self, 'title', data['title'])
        #add marking label and favour against

    def __eq__(self, other):
        return self.body == other.body

    def __repr__(self):
        return str(self.to_dict())

class TextCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text_id = db.Column(db.ForeignKey('text.id'))
    category_id = db.Column(db.ForeignKey('category.id'))
    cat_nr_dict = {'Unspecified':0, 'Atheism':1, 'Climate':2,
                  'Feminist':3, 'Hilary':4, 'Abortion':5}

    def __repr__(self):
        return '<Text id {} category id{}'.format(str(self.text_id),
                                                  str(self.category_id))

class Category(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    category_name = db.Column(db.String)

    def __repr__(self):
        return str(self.category_name)

class TextFavourAgainst(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text_id = db.Column(db.ForeignKey('text.id'))
    favour_against_id = db.Column(db.ForeignKey('favour_against.id'))

class FavourAgainst(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)