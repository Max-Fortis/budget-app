from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Category(db.Model):
    """Categories for transactions (e.g., Groceries, Transportation)"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    is_custom = db.Column(db.Boolean, default=False)
    budget_limit = db.Column(db.Float, default=0.0, server_default='0')

    # Relationship: one category can have many transactions
    transactions = db.relationship('Transaction', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'


class Transaction(db.Model):
    """Individual spending/income transactions"""
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    receipt_image = db.Column(db.String(300))  # Stores the filename of the receipt image

    # Foreign key linking to Category table
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    def __repr__(self):
        return f'<Transaction ${self.amount} - {self.description}>'


class Budget(db.Model):
    """Budget limits for tracking spending"""
    id = db.Column(db.Integer, primary_key=True)
    monthly_limit = db.Column(db.Float, nullable=False)
    weekly_limit = db.Column(db.Float)

    def __repr__(self):
        return f'<Budget Monthly: ${self.monthly_limit}>'
