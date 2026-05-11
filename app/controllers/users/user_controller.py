from flask import Blueprint, jsonify, request
from validators import email
from app.controllers.books.book_controller import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND
from app.controllers.companies.company_controller import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR
from app.models.users import User
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,create_access_token ,create_refresh_token ,
)
from app.extensions import db, bcrypt

users = Blueprint('users', __name__, url_prefix='/api/v1/users')


# ========================
# GET ALL USERS
# ========================
@users.get('/')
def getAllUsers():

    try:

        all_users = User.query.all()

        users_data = []

        for user in all_users:

            user_info = {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.first_name + " " + user.last_name,
                "email": user.email,
                "contact": user.contact,
                "type": user.user_type
            }

            users_data.append(user_info)

        return jsonify({
            "message": "All users retrieved successfully",
            "total_users": len(users_data),
            "users": users_data
        }), 200

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ========================
# GET ALL AUTHORS
# ========================
@users.get('/authors')
def getAllAuthors():

    try:

        all_authors = User.query.filter_by(
            user_type='author'
        ).all()

        authors_data = []

        for author in all_authors:

            author_info = {
                "id": author.id,
                "first_name": author.first_name,
                "last_name": author.last_name,
                "authorname": author.first_name + " " + author.last_name,
                "email": author.email,
                "contact": author.contact,
                "biography": author.biography,
                "created_at": author.created_at,
                "companies": [],
                "books": []
            }

            # ========================
            # AUTHOR BOOKS
            # ========================
            if hasattr(author, 'books'):

                author_info['books'] = [

                    {
                        "id": book.id,
                        "title": book.title,
                        "price": book.price,
                        "genre": book.genre,
                        "price_unit": book.price_unit,
                        "description": book.description,
                        "publication_date": book.publication_date,
                        "image": book.image,
                        "created_at": book.created_at
                    }

                    for book in author.books
                ]

            # ========================
            # AUTHOR COMPANIES
            # ========================
            if hasattr(author, 'companies'):

                author_info['companies'] = [

                    {
                        "id": company.id,
                        "name": company.name,
                        "origin": company.origin,
                        "description": company.description,
                    }

                    for company in author.companies
                ]

            authors_data.append(author_info)

        return jsonify({
            "message": "All authors retrieved successfully",
            "total_authors": len(authors_data),
            "authors": authors_data
        }), 200

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ========================
# GET USER BY ID
# ========================
@users.get('/<int:id>')
def getUserById(id):

    try:

        user = User.query.filter_by(id=id).first()

        if not user:
            return jsonify({
                "message": "User not found"
            }), 404

        # ========================
        # USER BOOKS
        # ========================
        books = []

        if hasattr(user, 'books'):

            books = [

                {
                    "id": book.id,
                    "title": book.title,
                    "price": book.price,
                    "price_unit": book.price_unit,
                    "genre": book.genre,
                    "description": book.description,
                    "publication_date": book.publication_date,
                    "image": book.image,
                    "created_at": book.created_at
                }

                for book in user.books
            ]

        # ========================
        # USER COMPANIES
        # ========================
        companies = []

        if hasattr(user, 'companies'):

            companies = [

                {
                    "id": company.id,
                    "name": company.name,
                    "origin": company.origin,
                    "description": company.description
                }

                for company in user.companies
            ]

        # ========================
        # USER DATA
        # ========================
        user_data = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.first_name + " " + user.last_name,
            "email": user.email,
            "contact": user.contact,
            "type": user.user_type,
            "biography": user.biography,
            "created_at": user.created_at,
            "companies": companies,
            "books": books
        }

        return jsonify({
            "message": "User details retrieved successfully",
            "user": user_data
        }), 200

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), HTTP_500_INTERNAL_SERVER_ERROR


# ========================
# UPDATE USER DETAILS
# ========================
@users.route('/<int:user_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def updateUser(user_id):

    try:
        data = request.get_json() or {}

        user = User.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({"message": "User not found"}), HTTP_404_NOT_FOUND

        current_user = int(get_jwt_identity())
        logged_in_user = User.query.filter_by(id=current_user).first()

        if not logged_in_user:
            return jsonify({"error": "User not found"}), HTTP_404_NOT_FOUND

        # ========================
        # AUTHORIZATION (VERY IMPORTANT)
        # ========================
        if logged_in_user.user_type != "admin" and current_user != user_id:
            return jsonify({"error": "Not authorized to update this user"}), HTTP_403_FORBIDDEN

        # ========================
        # DUPLICATE EMAIL CHECK
        # ========================
        new_email = data.get("email")

        if new_email and new_email != user.email:
            existing_user = User.query.filter_by(email=new_email).first()
            if existing_user:
                return jsonify({"error": "Email already in use"}), HTTP_409_CONFLICT

        # ========================
        # UPDATE FIELDS
        # ========================
        user.first_name = data.get("first_name", user.first_name)
        user.last_name = data.get("last_name", user.last_name)
        user.email = data.get("email", user.email)
        user.contact = data.get("contact", user.contact)
        user.biography = data.get("biography", user.biography)
        user.image = data.get("image", user.image)
    
        db.session.commit()

        return jsonify({
            "message": "User updated successfully",
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "contact": user.contact,
                "biography": user.biography,
                "image": user.image,
                "user_type": user.user_type
            }
        }), HTTP_200_OK

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR

    # DELETE USER
@users.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def deleteUser(user_id):

    try:
        user = User.query.filter_by(id=user_id).first()

        if not user:
            return jsonify({"message": "User not found"}), HTTP_404_NOT_FOUND

        current_user = int(get_jwt_identity())
        logged_in_user = User.query.filter_by(id=current_user).first()

        if not logged_in_user:
            return jsonify({"error": "User not found"}), HTTP_404_NOT_FOUND

        # AUTHORIZATION
        if logged_in_user.user_type != "admin" and current_user != user_id:
            return jsonify({"error": "Not authorized to delete this user"}), HTTP_403_FORBIDDEN

        db.session.delete(user)
        db.session.commit()

        return jsonify({
            "message": "User deleted successfully"
        }), HTTP_200_OK

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
    

    # SEARCH FOR AN AUTHOR
# SEARCH FOR AN AUTHOR
@users.get('/search')
def searchForAuthor():

    try:
        search_query = request.args.get('query')

        if not search_query:
            return jsonify({
                "message": "Search query is required"
            }), HTTP_400_BAD_REQUEST

        authors = User.query.filter(
            User.user_type == 'author',
            (
                User.first_name.ilike(f'%{search_query}%') |
                User.last_name.ilike(f'%{search_query}%')
            )
        ).all()

        if not authors:
            return jsonify({
                "message": f"No authors found matching '{search_query}'"
            }), HTTP_404_NOT_FOUND

        authors_data = []

        for author in authors:
            authors_data.append({
                "id": author.id,
                "first_name": author.first_name,
                "last_name": author.last_name,
                "author_name": f"{author.first_name} {author.last_name}",
                "email": author.email,
                "contact": author.contact,
                "biography": author.biography,
                "created_at": author.created_at
            })

        return jsonify({
            "message": "Authors retrieved successfully",
            "search_query": search_query,
            "total_results": len(authors_data),
            "authors": authors_data
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), HTTP_500_INTERNAL_SERVER_ERROR