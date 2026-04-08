from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from models import db, Category, Transaction, Budget
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import anthropic
import base64
from PIL import Image
import io

app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budget.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure file uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'heic'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize the database with the app
db.init_app(app)

# Initialize Anthropic client
anthropic_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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

    # Handle receipt image upload
    receipt_filename = None
    if 'receipt' in request.files:
        file = request.files['receipt']
        if file and file.filename != '' and allowed_file(file.filename):
            # Create a unique filename using timestamp
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            receipt_filename = f"{timestamp}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], receipt_filename))

    transaction = Transaction(
        amount=amount,
        category_id=category_id,
        description=description,
        receipt_image=receipt_filename
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


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded receipt images"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/extract_receipt', methods=['POST'])
def extract_receipt():
    """Extract transaction data from receipt image using Claude AI"""
    if 'receipt' not in request.files:
        return jsonify({'error': 'No receipt image provided'}), 400

    file = request.files['receipt']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400

    try:
        # Open and resize the image to keep it under 5MB
        img = Image.open(file.stream)

        # Convert RGBA to RGB if needed (for PNG with transparency)
        if img.mode == 'RGBA':
            img = img.convert('RGB')

        # Resize if too large (max width/height of 2048px should keep under 5MB)
        max_dimension = 2048
        if img.width > max_dimension or img.height > max_dimension:
            img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)

        # Convert to JPEG in memory with compression
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=85, optimize=True)
        img_byte_arr.seek(0)

        # Convert to base64
        image_data = base64.standard_b64encode(img_byte_arr.read()).decode('utf-8')
        media_type = 'image/jpeg'

        # Call Claude API with vision
        message = anthropic_client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": """Analyze this receipt and extract the following information in JSON format:
                            {
                                "amount": <total amount as a number>,
                                "merchant": "<merchant/store name>",
                                "date": "<date in YYYY-MM-DD format if visible, otherwise null>"
                            }

                            Only respond with valid JSON. If you cannot find certain information, use null."""
                        }
                    ],
                }
            ],
        )

        # Parse the response
        response_text = message.content[0].text

        # Try to extract JSON from the response
        import json
        import re

        # Claude might wrap JSON in markdown code blocks, so extract it
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON object directly
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            json_str = json_match.group(0) if json_match else response_text

        extracted_data = json.loads(json_str)

        return jsonify(extracted_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def init_default_categories():
    """Create default categories if they don't exist"""
    default_categories = ['Groceries', 'Transportation', 'Entertainment',
                         'Utilities', 'Dining Out', 'Shopping', 'Other']

    for cat_name in default_categories:
        if not Category.query.filter_by(name=cat_name).first():
            category = Category(name=cat_name, is_custom=False)
            db.session.add(category)

    db.session.commit()


@app.route('/scan')
def scan():
    """Receipt scanning / AI extraction page"""
    categories = Category.query.all()
    return render_template('scan.html', categories=categories)


@app.route('/budgets')
def budgets():
    """Budget overview page with per-category spending"""
    categories = Category.query.all()
    budget = Budget.query.first()

    now = datetime.now()
    month_start = datetime(now.year, now.month, 1)

    # Build per-category spending for current month
    category_data = []
    total_spent = 0
    for cat in categories:
        spent = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.category_id == cat.id,
            Transaction.date >= month_start
        ).scalar() or 0
        total_spent += spent
        category_data.append({
            'category': cat,
            'spent': spent,
            'limit': cat.budget_limit or 0,
            'pct': round((spent / cat.budget_limit * 100) if cat.budget_limit else 0)
        })

    # Spending history: last 10 days with amounts
    from collections import defaultdict
    history_raw = db.session.query(
        db.func.date(Transaction.date), db.func.sum(Transaction.amount)
    ).group_by(db.func.date(Transaction.date)).order_by(
        db.func.date(Transaction.date).desc()
    ).limit(10).all()
    history = list(reversed(history_raw))
    max_day = max((h[1] for h in history), default=1)

    monthly_limit = budget.monthly_limit if budget else 0
    remaining = monthly_limit - total_spent if budget else 0

    return render_template('budgets.html',
                           category_data=category_data,
                           budget=budget,
                           total_spent=total_spent,
                           remaining=remaining,
                           history=history,
                           max_day=max_day,
                           month_name=now.strftime('%B'),
                           categories=categories)


@app.route('/set_category_budget', methods=['POST'])
def set_category_budget():
    """Set budget limit for a category"""
    category_id = int(request.form['category_id'])
    limit = float(request.form['limit'])
    cat = Category.query.get(category_id)
    if cat:
        cat.budget_limit = limit
        db.session.commit()
    return redirect(url_for('budgets'))


@app.route('/styleguide')
def styleguide():
    """Design system style guide"""
    return render_template('styleguide.html')


if __name__ == '__main__':
    with app.app_context():
        # Create all database tables
        db.create_all()
        # Add budget_limit column to existing category tables (idempotent)
        try:
            db.session.execute(db.text(
                'ALTER TABLE category ADD COLUMN budget_limit FLOAT DEFAULT 0.0'
            ))
            db.session.commit()
        except Exception:
            pass  # Column already exists
        # Add default categories
        init_default_categories()

    # Run the app
    app.run(debug=True)
