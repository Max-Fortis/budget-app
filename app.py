from flask import Flask, render_template, request, redirect, url_for
from models import db, Category, Transaction, Budget
from datetime import datetime

app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budget.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)


@app.route('/')
def index():
    """Home page - shows all transactions and current budget status"""
    transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    categories = Category.query.all()
    budget = Budget.query.first()

    # Calculate total spending this month
    now = datetime.now()
    month_start = datetime(now.year, now.month, 1)
    monthly_spending = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.date >= month_start
    ).scalar() or 0

    return render_template('index.html',
                         transactions=transactions,
                         categories=categories,
                         budget=budget,
                         monthly_spending=monthly_spending)


@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    """Add a new transaction"""
    amount = float(request.form['amount'])
    category_id = int(request.form['category_id'])
    description = request.form.get('description', '')

    transaction = Transaction(
        amount=amount,
        category_id=category_id,
        description=description
    )

    db.session.add(transaction)
    db.session.commit()

    return redirect(url_for('index'))


@app.route('/add_category', methods=['POST'])
def add_category():
    """Add a new custom category"""
    name = request.form['name']

    category = Category(name=name, is_custom=True)

    db.session.add(category)
    db.session.commit()

    return redirect(url_for('index'))


@app.route('/set_budget', methods=['POST'])
def set_budget():
    """Set or update monthly budget"""
    monthly_limit = float(request.form['monthly_limit'])

    budget = Budget.query.first()
    if budget:
        budget.monthly_limit = monthly_limit
    else:
        budget = Budget(monthly_limit=monthly_limit)
        db.session.add(budget)

    db.session.commit()

    return redirect(url_for('index'))


def init_default_categories():
    """Create default categories if they don't exist"""
    default_categories = ['Groceries', 'Transportation', 'Entertainment',
                         'Utilities', 'Dining Out', 'Shopping', 'Other']

    for cat_name in default_categories:
        if not Category.query.filter_by(name=cat_name).first():
            category = Category(name=cat_name, is_custom=False)
            db.session.add(category)

    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        # Create all database tables
        db.create_all()
        # Add default categories
        init_default_categories()

    # Run the app
    app.run(debug=True)
