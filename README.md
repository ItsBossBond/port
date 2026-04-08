# Tharun.Dev — Portfolio Website

A dark-cyber styled developer portfolio built with Python/Flask.

## Features
- Animated 3D Three.js background
- Typewriter hero section
- Services, Pricing & Projects showcase
- Project Cost Estimator (terminal style)
- Contact form with CSRF protection
- Admin dashboard (messages, plans, calculator prices)
- Visitor analytics
- Mobile responsive

## Tech Stack
- **Backend**: Python, Flask, SQLAlchemy, Flask-Login, Flask-WTF
- **Frontend**: HTML5, CSS3 (custom), Vanilla JS, Three.js
- **DB**: SQLite (swap to PostgreSQL for production)
- **Fonts**: Syne + Space Mono

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run locally
```bash
python app.py
```

### 3. Deploy with Gunicorn
```bash
gunicorn app:app --bind 0.0.0.0:8000
```

## Environment Variables (optional)
| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | (hardcoded) | Flask secret key — **change in production!** |
| `ADMIN_EMAIL` | bcapro02@gmail.com | Admin login username |
| `ADMIN_PASSWORD` | passtosite@321 | Admin login password |

## Admin Panel
Visit `/login` and use your admin credentials.

## Project Structure
```
portfolio/
├── app.py              # Flask app, routes, models
├── requirements.txt
├── portfolio.db        # SQLite database (auto-created)
├── static/
│   ├── css/style.css   # All styles
│   └── js/main.js      # Three.js, typewriter, interactions
└── templates/
    ├── index.html      # Main portfolio page
    ├── login.html      # Admin login
    └── messages.html   # Admin dashboard
```
