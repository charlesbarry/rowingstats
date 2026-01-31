# Rowing Stats

A Django-based web application for tracking and analysing rowing competition statistics. The platform provides detailed tracking of rowers, races, results, and skill-based rankings using the TrueSkill algorithm.

## Overview

Rowing Stats tracks rowing competitions from major international events (Olympics, World Rowing Championships) to domestic regattas (Henley Royal Regatta, BUCS, Head of the River). Key features include:

- **Rower Profiles**: Search and browse rowers with full competition history
- **Race Tracking**: Multi-round tournament organisation with split times and metadata
- **TrueSkill Rankings**: Bayesian skill rating system with current and all-time rankings
- **Weather Corrections**: Physics-based speed adjustment calculations accounting for conditions
- **Knockout Predictions**: Match probability calculations for head-to-head racing
- **Data Import**: 30+ specialised importers for various regatta formats
- **Blog/Articles**: Content management system with Markdown support

## Tech Stack

- **Backend**: Django 4.2+ on Python 3.14
- **Database**: PostgreSQL (production) / SQLite (development)
- **Frontend**: Bootstrap 4, Django templates, AJAX autocomplete
- **Hosting**: Heroku with Gunicorn WSGI server
- **Static Files**: WhiteNoise with compression

## Project Structure

```
rowingstats/
├── rowingstats/      # Django project configuration
├── rowing/           # Core application (rowers, races, rankings)
├── blog/             # Article publishing system
├── hrr/              # Head of the River experimental app
├── scripts/          # Data import and processing utilities
└── requirements.txt  # Python dependencies
```

## Installation

### Prerequisites

- Python 3.12+ (developed on 3.14)
- PostgreSQL (recommended) or SQLite

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rowingstats
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file in `rowingstats/rowingstats/` (alongside `settings.py`) with:
   ```
   SECRET_KEY=your-secure-random-string-here
   DEBUG=True
   DATABASE_URL=postgres://user:password@localhost:5432/rowingstats  # Optional
   ```

   If `DATABASE_URL` is not specified, SQLite will be used. Note that some features are optimised for PostgreSQL.

5. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```

   Navigate to `http://localhost:8000`

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | - | Django secret key |
| `DATABASE_URL` | No | SQLite | PostgreSQL connection string |
| `DEBUG` | No | `False` | Enable debug mode |
| `SESSION_COOKIE_SECURE` | No | `True` | Secure session cookies |
| `CSRF_COOKIE_SECURE` | No | `True` | Secure CSRF cookies |
| `RSPLATFORM` | No | - | Set to `heroku` for production |

## Deployment

The application is configured for Heroku deployment:

```bash
# Procfile runs migrations automatically on release
heroku create your-app-name
git push heroku main
```

## Key Management Commands

```bash
# Recalculate TrueSkill scores
python manage.py recalculator

# Run tests
python manage.py test

# Collect static files
python manage.py collectstatic
```

## Security

Recent security improvements include:
- HSTS with preload enabled
- Secure cookie configuration
- XSS protection headers
- Content-Type sniffing prevention
- Bleach-sanitised Markdown rendering