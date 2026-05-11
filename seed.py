# from app import create_app
# from app.extensions import db
# from app.models import User , Company , Book
# from werkzeug.security import generate_password_hash
from app import create_app
from app.extensions import db
from app.models.users import User
from app.models.companies import Company
from app.models.books import Book
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():

    print("🌱 Seeding realistic data...")

    # ========================
    # CLEAR OLD DATA
    # ========================
    Company.query.delete()
    Book.query.delete()
    User.query.delete()
    db.session.commit()

    # ========================
    # REALISTIC USERS DATA
    # ========================
    users_data = [
        ("John", "Doe", "john@gmail.com"),
        ("Sarah", "Kato", "sarah@gmail.com"),
        ("David", "Moses", "david@gmail.com"),
        ("Grace", "Nakamya", "grace@gmail.com"),
        ("Brian", "Otim", "brian@gmail.com"),
        ("Lydia", "Nabirye", "lydia@gmail.com"),
        ("Michael", "Sserwadda", "michael@gmail.com"),
        ("Joy", "Achieng", "joy@gmail.com"),
        ("Steven", "Mutebi", "steven@gmail.com"),
        ("Ann", "Nabukenya", "ann@gmail.com"),
        ("Daniel", "Kintu", "daniel@gmail.com"),
        ("Patricia", "Nakato", "patricia@gmail.com"),
        ("Andrew", "Mugisha", "andrew@gmail.com"),
        ("Faith", "Auma", "faith@gmail.com"),
        ("Samuel", "Kato", "samuel@gmail.com"),
        ("Christine", "Nalubega", "christine@gmail.com"),
        ("Eric", "Ssentongo", "eric@gmail.com"),
        ("Susan", "Nanyonga", "susan@gmail.com"),
        ("Joseph", "Okello", "joseph@gmail.com"),
        ("Brenda", "Nabwire", "brenda@gmail.com"),
    ]

    users = []

    # ========================
    # CREATE USERS
    # ========================
    for first, last, email in users_data:

        user = User(
            first_name=first,
            last_name=last,
            email=email,
            contact="0700000000",
            password=generate_password_hash("12345678"),
            biography=f"{first} is a software developer and author.",
            user_type="author"
        )

        db.session.add(user)
        users.append(user)

    db.session.commit()

    print("👤 20 users created")

    # ========================
    # COMPANIES (1–2 per user)
    # ========================
    company_names = [
        "TechNova Ltd", "ByteWorks", "CloudCore Systems",
        "DevHouse Africa", "NextGen Solutions", "AlphaTech",
        "CodeCrafters", "DataNest", "SoftLink Uganda"
    ]

    for i, user in enumerate(users):

        company = Company(
            name=company_names[i % len(company_names)],
            origin="Uganda",
            user_id=user.id
        )

        db.session.add(company)

    db.session.commit()

    print(" Companies created")

    # ========================
    # BOOKS
    # ========================
    book_titles = [
        "Python Basics",
        "Flask for Beginners",
        "Mastering APIs",
        "Database Design",
        "Web Development Guide"
    ]

    for i, user in enumerate(users):

        book = Book(
            title=book_titles[i % len(book_titles)],
            price=20 + i,
            genre="Technology",
            description=f"{book_titles[i % len(book_titles)]} by {user.first_name}",
            price_unit="USD",
            publication_date="2026-01-01",
            image="default.png",
            user_id=user.id
        )

        db.session.add(book)

    db.session.commit()

    print("📚 Books created")

    print("✅ SEEDING COMPLETED SUCCESSFULLY (20 users + companies + books)")