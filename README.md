# DevOps - Homework 1 - Cookie Jar

## Context 
The application used in this homework is inspired by an operational data engineering project I am currently developing for a client, which will likely become the foundation for my Master’s thesis. 
The broader project addresses GDPR-driven transparency requirements in digital marketing.

For the purpose of this homework, I created an **extremely simplified** version that focuses on a **minimal set of operations** and includes a small HTML UI to make the outcome easy to visualize. The database is seeded from a CSV file representing an **anonymized** version of a real tracker scan received from a third-party provider (TrustArc).

---

## Tech stack
- **Backend:** Flask (Python)
- **ORM:** SQLAlchemy
- **Database:** PostgreSQL (primarily) / SQLite
- **UI:** simple HTML pages

---

## Project structure 
- `cookiejar/`: application package (models → DAOs → services → routes) plus `templates/` and `static/` for the minimal HTML UI.
- `data/`: anonymized CSV seed file used to populate the database.
- `migrations/`: Flask-Migrate/Alembic migration scripts and metadata for versioning/applying schema changes.
- `app.py`: application entry point that creates and starts the Flask app.
- `config.py`: configuration (including SQLAlchemy connection string via `DATABASE_URL`).


## Database schema
![Homework database schema](cookiejar/static/db_schema.png)
