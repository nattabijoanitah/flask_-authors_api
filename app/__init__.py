from flask import Flask
from app.extensions import db, migrate, bcrypt
from app.controllers.auth.auth_controller import auth

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    from app.models.users import User
    from app.models.companies import Company
    from app.models.books import Book

    app.register_blueprint(auth)

    @app.route('/')
    def home():
        return "Authors API project setup"

    return app