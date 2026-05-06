print("Loading User model...")
from app.extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100),  nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    contact = db.Column(db.String(50), unique=True, nullable=False)
    image = db.Column(db.String(200), nullable=False)
    password = db.Column(db.Text(100), nullable=False)
    biography = db.Column(db.Text(500), nullable=False)
    user_type = db.Column(db.String(20), default="author", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())


    def __init__(self , first_name, last_name, email, contact, password, biography, user_type , image=None):
        
        super(User, self).__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.contact = contact
        self.image = image
        self.password = password
        self.biography = biography
        self.user_type = user_type

    def get_full_name(self):
            return f"{self.first_name} {self.last_name}"
print("User model loaded successfully")