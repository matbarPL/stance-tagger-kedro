from flask import Flask
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

app = Flask(__name__)
jwt = JWTManager(app)
app.config.from_object(Config)
app.config['JWT_SECRET_KEY'] = 'super-secret'
db = SQLAlchemy(app)

migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

app.debug = True
from app.api import bp as api_bp
app.register_blueprint(api_bp, url_prefix='/api')


if __name__=="__main__":
    app.run()