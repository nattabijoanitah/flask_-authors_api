from flask import Blueprint, request, jsonify
import validators
from app.models.users import User
from app.extensions import db, bcrypt

# Remove the status_codes import entirely and replace with these:
HTTP_201_CREATED = 201
HTTP_400_BAD_REQUEST = 400
HTTP_409_CONFLICT = 409
HTTP_500_INTERNAL_SERVER_ERROR = 500

auth = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}

    first_name = data.get('first_name')
    last_name = data.get('last_name')
    contact = data.get('contact')
    email = data.get('email')
    user_type = data.get('type')
    password = data.get('password')
    biography = data.get('biography', '') if user_type == "author" else ''

    # validation
    if not first_name or not last_name or not contact or not password or not email:
        return jsonify({"error": "All fields are required"}), HTTP_400_BAD_REQUEST

    if user_type == 'author' and not biography:
        return jsonify({"error": "Enter your author biography"}), HTTP_400_BAD_REQUEST

    if len(password) < 8:
        return jsonify({"error": "Password is too short"}), HTTP_400_BAD_REQUEST

    if not validators.email(email):
        return jsonify({"error": "Email address is not valid"}), HTTP_400_BAD_REQUEST

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email address in use"}), HTTP_409_CONFLICT

    if User.query.filter_by(contact=contact).first():
        return jsonify({"error": "Contact number in use"}), HTTP_409_CONFLICT

    try:
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            contact=contact,
            password=hashed_password,
            biography=biography,
            user_type=user_type
        )

        db.session.add(new_user)
        db.session.commit()

        username = new_user.get_full_name()

        return jsonify({
            "message": f"{username} has been successfully created as an {new_user.user_type}",
            "user": {
                "id": new_user.id,
                "first_name": new_user.first_name,
                "last_name": new_user.last_name,
                "email": new_user.email,
                "contact": new_user.contact,
                "biography": new_user.biography,
                "user_type": new_user.user_type,
                "created_at": new_user.created_at,
                "updated_at": new_user.updated_at
            }
        }), HTTP_201_CREATED

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR