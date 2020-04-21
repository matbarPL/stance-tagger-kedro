from app.api import bp
from flask import jsonify
from app.models import User
from flask import request
from app.api.errors import bad_request
from flask import url_for
from app import db
from flask import g, abort
from app.api.auth import token_auth

@bp.route('/kedro/run', methods=['POST'])
@token_auth.login_required
def kedro_run(id):

    return

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
    if 'username' not in data or 'password' not in data:
        return bad_request('must include username and password fields')
    user = User.query.filter_by(username=data['username']).first()
    if not user.check_password(data['password']) or user is None:
        response = jsonify({"error": "Invalid username or password"})
    else:
        response = jsonify({'token': user.get_token()})
        response.status_code = 201
        response.headers['Location'] = url_for('api.login_user', id=user.id)
    print (response.data)
    return response


@bp.route('/users/register', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return bad_request('must include username, email and password fields')
    if User.query.filter_by(username=data['username']).first():
        return bad_request('please use a different username')
    if User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response

@bp.route('/users/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_user(id):
    if g.current_user.id != id:
        abort(403)
    user = User.query.get_or_404(id)
    data = request.get_json() or {}
    if 'username' in data and data['username'] != user.username and \
            User.query.filter_by(username=data['username']).first():
        return bad_request('please use a different username')
    if 'email' in data and data['email'] != user.email and \
            User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    user.from_dict(data, new_user=False)
    db.session.commit()
    return jsonify(user.to_dict())

