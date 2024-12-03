from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    master_password_hash = db.Column(db.String(128), nullable=False)
    security_questions = db.relationship('SecurityQuestion', backref='user', lazy=True)

    def set_master_password(self, password):
        self.master_password_hash = generate_password_hash(password)

    def check_master_password(self, password):
        return check_password_hash(self.master_password_hash, password)

class SecurityQuestion(db.Model):
    __tablename__ = 'security_questions'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    answer_hash = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def set_answer(self, answer):
        self.answer_hash = generate_password_hash(answer)

    def check_answer(self, answer):
        return check_password_hash(self.answer_hash, answer)

class VaultItem(db.Model):
    __tablename__ = 'vault_items'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_type = db.Column(db.String(50), nullable=False)  # 'Login', 'Credit Card', 'Identity', 'Secure Note'
    name = db.Column(db.String(120), nullable=False)  # Friendly name for the item
    details = db.relationship('VaultDetail', backref='vault_item', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

class VaultDetail(db.Model):
    __tablename__ = 'vault_details'
    id = db.Column(db.Integer, primary_key=True)
    vault_item_id = db.Column(db.Integer, db.ForeignKey('vault_items.id'), nullable=False)
    key = db.Column(db.String(120), nullable=False)  # Example: 'username', 'password', 'credit_card_number'
    value = db.Column(db.String(255), nullable=False)  # Sensitive data encrypted before storage

    def set_value(self, value):
        self.value = encrypt_data(value)

    def get_value(self):
        return decrypt_data(self.value)

# Replace with a secure key management approach
SECRET_KEY = Fernet.generate_key()
cipher = Fernet(SECRET_KEY)

def encrypt_data(data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    return cipher.encrypt(data).decode('utf-8')

def decrypt_data(data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    return cipher.decrypt(data).decode('utf-8')
