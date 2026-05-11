from flask import Flask
from app.extensions import db, migrate, bcrypt, jwt
from app.controllers.auth.auth_controller import auth
from app.controllers.users.user_controller import users
from flask_jwt_extended import create_access_token
from app.controllers.companies.company_controller import companies
from app.controllers.books.book_controller import books
def create_app():
    app = Flask(__name__)

    app.config.update(
        SECRET_KEY="super_secret_key",
        JWT_SECRET_KEY="jwt-super-secret-key",
        SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:@localhost/flask_authors_db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)

    from app.models.users import User
    from app.models.companies import Company
    from app.models.books import Book

    app.register_blueprint(auth)
    app.register_blueprint(users)
    app.register_blueprint(companies)
    app.register_blueprint(books)

    @app.route('/')
    def home():
        return "Authors API project setup"

    return app