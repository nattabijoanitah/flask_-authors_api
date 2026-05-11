from flask import Blueprint, request, jsonify
import validators
from app.models.users import User
from app.extensions import db, bcrypt
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)

auth = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

HTTP_201_CREATED = 201
HTTP_400_BAD_REQUEST = 400
HTTP_409_CONFLICT = 409
HTTP_500_INTERNAL_SERVER_ERROR = 500
HTTP_401_UNAUTHORIZED = 401
HTTP_200_OK = 200



# REGISTER

@auth.route('/register', methods=['POST'])
def register():

    data = request.get_json() or {}

    first_name = data.get('first_name')
    last_name = data.get('last_name')
    contact = data.get('contact')
    email = data.get('email')
    user_type = data.get('user_type', 'author')
    password = data.get('password')

    biography = data.get('biography') if user_type == "author" else ''
    image = data.get('image') or 'default.png'

    if not all([first_name, last_name, contact, email, password]):
        return jsonify({"error": "Allvggg fields are required"}), HTTP_400_BAD_REQUEST

    if user_type == 'author' and not biography:
        return jsonify({"error": "Enter your author biography"}), HTTP_400_BAD_REQUEST

    if len(password) < 8:
        return jsonify({"error": "Password is too short"}), HTTP_400_BAD_REQUEST

    if not validators.email(email):
        return jsonify({"error": "Invalid email address"}), HTTP_400_BAD_REQUEST

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already in use"}), HTTP_409_CONFLICT

    if User.query.filter_by(contact=contact).first():
        return jsonify({"error": "Contact already in use"}), HTTP_409_CONFLICT

    try:
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            contact=contact,
            password=hashed_password,
            biography=biography,
            user_type=user_type,
            image=image
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "message": f"{first_name} {last_name} created successfully as {user_type}",
            "user": {
                "id": new_user.id,
                "first_name": new_user.first_name,
                "last_name": new_user.last_name,
                "email": new_user.email,
                "contact": new_user.contact,
                "biography": new_user.biography,
                "user_type": new_user.user_type,
                "image": new_user.image
            }
        }), HTTP_201_CREATED

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR


# LOGIN

@auth.route('/login', methods=['POST'])
def login():

    data = request.get_json() or {}

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), HTTP_400_BAD_REQUEST

    try:
        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({"message": "Invalid email address"}), HTTP_401_UNAUTHORIZED

        if not bcrypt.check_password_hash(user.password, password):
            return jsonify({"message": "Invalid password"}), HTTP_401_UNAUTHORIZED

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return jsonify({
            "user": {
                "id": user.id,
                "username": f"{user.first_name} {user.last_name}",
                "email": user.email,
                "user_type": user.user_type
            },
            "access_token": access_token,
            "refresh_token": refresh_token,
            "message": "You have successfully logged into your account"
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR



# REFRESH TOKEN
@auth.route('/token/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)

    return jsonify({
        "access_token": access_token
    }), HTTP_200_OK



# PROFILE (PROTECTED)

@auth.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    return jsonify({"message": "Access granted"}), HTTP_200_OK