from app.api import bp
from flask import jsonify, redirect
from app.models import User
from flask import request
from app.api.errors import bad_request
from flask import url_for
from app import db
from flask import g
from app.api.auth import token_auth

@bp.route('/users/<int:id>', methods=['GET'])
@token_auth.login_required
def get_user(id):
    return jsonify(User.query.get_or_404(id).to_dict())

@bp.route('/users', methods=['GET'])
@token_auth.login_required
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(User.query, page, per_page, 'api.get_users')
    return jsonify(data)

@bp.route('/users/login', methods=['POST'])
def login_user():
    data = request.get_json() or {}
    if 'email' not in data or 'password' not in data:
        return bad_request('Invalid form')
    user = User.query.filter_by(email=data['email']).first()
    if user is None:
        return False
    if not user.check_password(data['password']):
        response = jsonify({"error": "Invalid username or password"})
    else:
        g.current_user = user
        response = jsonify({'token': user.get_token()})
        response.status_code = 201
        response.headers['Location'] = url_for('api.login_user', id=user.id)
    return response

@bp.route('/users/register', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    if 'first_name' not in data or 'last_name' not in data or 'password' not in data:
        return bad_request('Invalid form')
    if User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email')
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response

@bp.route('/users/update', methods=['PUT'])
def update_user():
    data = request.get_json() or {}
    user = User.check_token(data['token'])
    user.from_dict(data, new_user=False)
    user.get_token()
    db.session.commit()
    return jsonify(user.to_dict())