from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from fastjob.config import Config


db = SQLAlchemy()
bcrypt = Bcrypt()
login_Manager = LoginManager()
login_Manager.login_view = 'users.login'
login_Manager.login_message_category = 'info'
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_Manager.init_app(app)
    mail.init_app(app)

    from fastjob.users.routes import users
    from fastjob.posts.routes import posts
    from fastjob.main.routes import main

    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)

    return app





