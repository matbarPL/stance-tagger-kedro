from flask import Flask
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_dance.contrib.twitter import make_twitter_blueprint

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
twitter_blueprint = make_twitter_blueprint(api_key='YKBGyqhWgdYnSG9jMgwGnHaKo',
                                           api_secret='CGgGn4PMRxlDs1wJ7vdIhvvrEJXdkOMs3N3edupYddCyT5NHgj')
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(twitter_blueprint, url_prefix='/twitter_login')

if __name__=="__main__":
    app.run()