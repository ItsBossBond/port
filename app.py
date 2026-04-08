import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
from datetime import datetime, timedelta

app = Flask(__name__, template_folder='templates', static_folder='static')

# --- CONFIGURATION ---
# IMPORTANT: Change this secret key before deploying to production!
app.secret_key = os.environ.get('SECRET_KEY', 'CHANGE_THIS_TO_A_VERY_LONG_RANDOM_STRING_FOR_PRODUCTION')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

# --- DATABASE ---
db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'portfolio.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

# --- EXTENSIONS ---
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access the admin panel.'
login_manager.login_message_category = 'error'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# --- MODELS ---
class User(UserMixin, db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class ContactMessage(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.String(150), nullable=False)
    message      = db.Column(db.Text, nullable=False)
    timestamp    = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    replied      = db.Column(db.Boolean, default=False)
    replied_at   = db.Column(db.DateTime, nullable=True)
    reply_content = db.Column(db.Text, nullable=True)

class Visitor(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50))
    timestamp  = db.Column(db.DateTime, default=datetime.utcnow, index=True)

class ServicePlan(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    title      = db.Column(db.String(100), nullable=False)
    price      = db.Column(db.String(50), nullable=False)
    unit       = db.Column(db.String(50), default='')
    features   = db.Column(db.Text, default='')
    is_popular = db.Column(db.Boolean, default=False)
    btn_text   = db.Column(db.String(50), default='SELECT')

class CalculatorOption(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    label       = db.Column(db.String(100), nullable=False)
    price_value = db.Column(db.Integer, nullable=False)

# --- VISITOR TRACKING ---
@app.before_request
def track_visitor():
    if request.endpoint == 'home' and 'visited' not in session:
        try:
            # Support X-Forwarded-For for proxied deployments
            visitor_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            if visitor_ip:
                visitor_ip = visitor_ip.split(',')[0].strip()
            db.session.add(Visitor(ip_address=visitor_ip))
            db.session.commit()
            session['visited'] = True
        except Exception:
            db.session.rollback()

# --- ROUTES ---
@app.route('/')
def home():
    plans       = ServicePlan.query.all()
    calc_options = CalculatorOption.query.all()

    services = [
        {"title": "Full Stack Web Dev",   "desc": "Custom Python/Flask backends with dynamic HTML/JS frontends.", "icon": "💻"},
        {"title": "Crypto Tool Scripts",  "desc": "High-performance scripts, automation tools, and flash software.", "icon": "⚡"},
        {"title": "API Integration",      "desc": "Connecting payment gateways, crypto nodes, and third-party APIs.", "icon": "🔗"},
        {"title": "Bug Fixing & Hosting", "desc": "Fixing code errors and deploying to AWS, Koyeb, or Render.", "icon": "🛠️"},
    ]

    projects = [
        {
            "title": "Flash USDT Shop",
            "tech": "Flask, SQLite",
            "img": "https://images.unsplash.com/photo-1621416894569-0f39ed31d247?auto=format&fit=crop&w=500&q=60"
        },
        {
            "title": "Trading Bot V1",
            "tech": "Python, Binance API",
            "img": "https://images.unsplash.com/photo-1611974765270-ca1258634369?auto=format&fit=crop&w=500&q=60"
        },
        {
            "title": "Admin Dashboard",
            "tech": "React, Node.js",
            "img": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=500&q=60"
        },
    ]

    return render_template('index.html', services=services, projects=projects,
                           plans=plans, calc_options=calc_options)

@app.route('/send_message', methods=['POST'])
def send_message():
    name        = request.form.get('name', '').strip()
    contact     = request.form.get('contact', '').strip()
    msg_content = request.form.get('message', '').strip()

    if not name or not contact or not msg_content:
        flash('All fields are required.', 'error')
        return redirect(url_for('home', _anchor='contact'))

    if len(name) > 100 or len(contact) > 150 or len(msg_content) > 2000:
        flash('Input exceeds allowed length.', 'error')
        return redirect(url_for('home', _anchor='contact'))

    try:
        new_msg = ContactMessage(name=name, contact_info=contact, message=msg_content)
        db.session.add(new_msg)
        db.session.commit()
        flash('Message sent! I will get back to you shortly.', 'success')
    except Exception:
        db.session.rollback()
        flash('Something went wrong. Please try again.', 'error')

    return redirect(url_for('home', _anchor='contact'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user, remember=False)
            session.permanent = True
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin_dashboard'))

        flash('Invalid credentials. Please try again.', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

@app.route('/admin')
@login_required
def admin_dashboard():
    messages     = ContactMessage.query.order_by(ContactMessage.timestamp.desc()).all()
    plans        = ServicePlan.query.all()
    calc_options = CalculatorOption.query.all()

    now         = datetime.utcnow()
    day_start   = now - timedelta(days=1)
    week_start  = now - timedelta(weeks=1)
    month_start = now - timedelta(days=30)

    stats = {
        'day':   Visitor.query.filter(Visitor.timestamp >= day_start).count(),
        'week':  Visitor.query.filter(Visitor.timestamp >= week_start).count(),
        'month': Visitor.query.filter(Visitor.timestamp >= month_start).count(),
    }

    return render_template('messages.html', messages=messages, stats=stats,
                           plans=plans, calc_options=calc_options)

# --- ADMIN ACTIONS ---
@app.route('/admin/add_plan', methods=['POST'])
@login_required
def add_plan():
    title      = request.form.get('title', '').strip()
    price      = request.form.get('price', '').strip()
    unit       = request.form.get('unit', '').strip()
    features   = request.form.get('features', '').strip()
    btn_text   = request.form.get('btn_text', 'SELECT').strip() or 'SELECT'
    is_popular = bool(request.form.get('is_popular'))

    if not title or not price or not features:
        flash('Title, price and features are required.', 'error')
        return redirect(url_for('admin_dashboard'))

    try:
        new_plan = ServicePlan(title=title, price=price, unit=unit,
                               features=features, is_popular=is_popular, btn_text=btn_text)
        db.session.add(new_plan)
        db.session.commit()
        flash(f'Plan "{title}" added successfully.', 'success')
    except Exception:
        db.session.rollback()
        flash('Error adding plan.', 'error')

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_plan/<int:plan_id>', methods=['POST'])
@login_required
def delete_plan(plan_id):
    plan = db.session.get(ServicePlan, plan_id)
    if plan:
        try:
            db.session.delete(plan)
            db.session.commit()
            flash(f'Plan "{plan.title}" deleted.', 'success')
        except Exception:
            db.session.rollback()
            flash('Error deleting plan.', 'error')
    else:
        flash('Plan not found.', 'error')

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/update_calc', methods=['POST'])
@login_required
def update_calc():
    opt_id    = request.form.get('opt_id')
    new_price = request.form.get('price_value')

    if not opt_id or not new_price:
        flash('Missing data.', 'error')
        return redirect(url_for('admin_dashboard'))

    opt = db.session.get(CalculatorOption, int(opt_id))
    if opt:
        try:
            opt.price_value = max(0, int(new_price))
            db.session.commit()
            flash(f'"{opt.label}" price updated to ${opt.price_value}.', 'success')
        except (ValueError, Exception):
            db.session.rollback()
            flash('Invalid price value.', 'error')
    else:
        flash('Option not found.', 'error')

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_msg/<int:msg_id>', methods=['POST'])
@login_required
def delete_msg(msg_id):
    msg = db.session.get(ContactMessage, msg_id)
    if msg:
        try:
            db.session.delete(msg)
            db.session.commit()
            flash('Message deleted.', 'success')
        except Exception:
            db.session.rollback()
            flash('Error deleting message.', 'error')
    else:
        flash('Message not found.', 'error')

    return redirect(url_for('admin_dashboard'))

# --- HEALTH CHECK ---
@app.route('/ping')
def ping():
    return 'Pong', 200

# --- DB INIT & SEED ---
with app.app_context():
    db.create_all()

    # Create default admin if not present
    admin_email = os.environ.get('ADMIN_EMAIL', 'bcapro02@gmail.com')
    admin_pass  = os.environ.get('ADMIN_PASSWORD', 'passtosite@321')
    if not User.query.filter_by(username=admin_email).first():
        hashed = generate_password_hash(admin_pass, method='pbkdf2:sha256')
        db.session.add(User(username=admin_email, password=hashed))
        db.session.commit()

    # Seed service plans
    if not ServicePlan.query.first():
        seed_plans = [
            ServicePlan(title='CODE FIX & SUPPORT', price='$50', unit='/hour',
                        features='Python/Flask Bug Fixes,Server Deployment,DB Connection Issues',
                        btn_text='FIX MY CODE'),
            ServicePlan(title='CUSTOM WEBSITE', price='$300', unit='/start',
                        features='Professional Portfolio,Mobile Responsive,Contact Form,Neon Styling',
                        is_popular=True, btn_text='BUILD THIS'),
            ServicePlan(title='FULL WEB APP', price='$800', unit='/project',
                        features='Complete Backend,User Login System,Database & Payments,Crypto/API Integration',
                        btn_text='START PROJECT'),
        ]
        db.session.add_all(seed_plans)
        db.session.commit()

    # Seed calculator options
    if not CalculatorOption.query.first():
        seed_opts = [
            CalculatorOption(label='Basic Website',      price_value=100),
            CalculatorOption(label='Custom Backend',     price_value=200),
            CalculatorOption(label='Database Setup',     price_value=200),
            CalculatorOption(label='Crypto Integration', price_value=200),
            CalculatorOption(label='Hosting & Deploy',   price_value=150),
        ]
        db.session.add_all(seed_opts)
        db.session.commit()

@app.route("/reset-db")
def reset_db():
    db.drop_all()
    db.create_all()
    return "Database reset successful"

if __name__ == '__main__':
    app.run(debug=False)
