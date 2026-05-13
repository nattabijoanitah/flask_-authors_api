import email

from flask import Blueprint, request, jsonify
from sqlalchemy import all_
import validators
from app.models.companies import Company
from app.models.users import User
from app.extensions import db, bcrypt
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)

from app.status_codes import HTTP_404_NOT_FOUND

from app.status_codes import HTTP_404_NOT_FOUND
from app.models.users import User
# Company Blueprint
companies = Blueprint('companies', __name__, url_prefix='/api/v1/companies')

HTTP_201_CREATED = 201
HTTP_400_BAD_REQUEST = 400
HTTP_409_CONFLICT = 409
HTTP_500_INTERNAL_SERVER_ERROR = 500
HTTP_401_UNAUTHORIZED = 401
HTTP_200_OK = 200



# CREATING COMPANIES

@companies.route('/create', methods=['POST'])
@jwt_required()
def createCompany():

# STORING REQUEST VALUES IN VARIABLES
    data = request.get_json() or {}

    origin = data.get('origin')
    description = data.get('description')
    user_id = get_jwt_identity()
    name = data.get('name')

    # VALIDATIONS OF THE INCOMING REQUEST
    
    if not all([origin, description, name]): 
        return jsonify({"error": "All fields are required"}), HTTP_400_BAD_REQUEST

    if Company.query.filter_by(name=name).first() is not None:
        return jsonify({"error": "Company name already in use"}), HTTP_409_CONFLICT


    # CREATING A NEW COMPANY INSTANCE AND STORING IT IN THE DATABASE

    try:

        new_company = Company(
            origin=origin,
            description=description,
            name=name,
            user_id=user_id
               
        )

        db.session.add(new_company)
        db.session.commit()

        return jsonify({
            "message": f"{origin} created successfully",
            "company    ": {
                "id": new_company.id,
                "name": new_company.name,
                "origin": new_company.origin,
                "description": new_company.description,
                "user_id": new_company.user_id
            }
        }), HTTP_201_CREATED

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
    

    # RETRIEVING ALL COMPANIES
@companies.route('/', methods=['GET'])
def getAllCompanies():

    try:

        all_companies = Company.query.all()

        companies_data = []

        for company in all_companies:

            company_info = {
                "id": company.id,
                "name": company.name,
                "origin": company.origin,
                "description": company.description,
                "user_id": company.user_id
            }

            # SAFE USER CHECK
            if company.user:

                company_info["user"] = {
                    "id": company.user.id,
                    "first_name": company.user.first_name,
                    "last_name": company.user.last_name,
                    "email": company.user.email,
                    "contact": company.user.contact,
                    "biography": company.user.biography,
                    "user_type": company.user.user_type,
                    "image": company.user.image,
                    "created_at": company.user.created_at,
                    "updated_at": company.user.updated_at
                }

            companies_data.append(company_info)

        return jsonify({
            "message": "All companies retrieved successfully",
            "total_companies": len(companies_data),
            "companies": companies_data
        }), HTTP_200_OK

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), HTTP_500_INTERNAL_SERVER_ERROR


# GET A COMPANY BY ID
@companies.route('/<int:company_id>', methods=['GET'])
def getCompanyById(company_id):

    try:
    
        company = Company.query.get(company_id)

        if not company:
            return jsonify({"message": "Company not found"}),   HTTP_404_NOT_FOUND

        company_info = {
            "id": company.id,
            "name": company.name,
            "origin": company.origin,
            "description": company.description,
            "user_id": company.user_id
        }

        # SAFE USER CHECK
        if company.user:

            company_info["user"] = {
                "id": company.user.id,
                "first_name": company.user.first_name,
                "last_name": company.user.last_name,
                "email": company.user.email,
                "contact": company.user.contact,
                "biography": company.user.biography,
                "user_type": company.user.user_type,
                "image": company.user.image,
                "created_at": company.user.created_at,
                "updated_at": company.user.updated_at
            }

        return jsonify({
            "message": f"Company with id {company_id} retrieved successfully",
            "company":company_info            
        }), HTTP_200_OK
    except Exception as e:
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
# UPDATING A COMPANY
@companies.route('/<int:company_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def updateCompany(company_id):

    try:
        data = request.get_json() or {}

        company = Company.query.get(company_id)

        if not company:
            return jsonify({"message": "Company not found"}), HTTP_404_NOT_FOUND

        # FIXED AUTH CHECK
        current_user_id = int(get_jwt_identity())

        if company.user_id != current_user_id:
            return jsonify({
                "message": "Unauthorized to update this company"
            }), HTTP_401_UNAUTHORIZED

        # UPDATE FIELDS
        company.name = data.get('name', company.name)
        company.origin = data.get('origin', company.origin)
        company.description = data.get('description', company.description)

        db.session.commit()

        return jsonify({
            "message": f"Company with id {company_id} updated successfully",
            "company": {
                "id": company.id,
                "name": company.name,
                "origin": company.origin,
                "description": company.description,
                "user_id": company.user_id
            }
        }), HTTP_200_OK

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR

        # DELETING A COMPANY 
@companies.route('/delete/<int:company_id>', methods=['DELETE'])
@jwt_required()
def deleteCompany(company_id):

    try:
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        company = Company.query.filter_by(id=company_id).first()

        if not user:
            return jsonify({"message": "User not found"}), HTTP_404_NOT_FOUND

        # AUTHORISATION  CHECK
        if user.user_type != "admin" and user.id != current_user_id:
            return jsonify({"message": "Unauthorized to delete this company"}), HTTP_401_UNAUTHORIZED
        
        # DELETE ASSOCIATED BOOKS FIRST (CASCADE DELETE)
        for book in company.books:
            db.session.delete(book)


#       # DELETE THE COMPANY
        db.session.delete(company)
        db.session.commit()

        return jsonify({
            "message": f"Company with id {company_id} deleted successfully"
        }), HTTP_200_OK

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), HTTP_500_INTERNAL_SERVER_ERROR
    
