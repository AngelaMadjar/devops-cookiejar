# DevOps - Homework 1 - Cookie Jar

## Context 
The application used in this homework is inspired by an operational data engineering project I am currently developing for a client, which will likely become the foundation for my Master’s thesis. 
The broader project addresses GDPR-driven transparency requirements in digital marketing.

For the purpose of this homework, I created an **extremely simplified** version that focuses on a **minimal set of operations** and includes a small HTML UI to make the outcome easy to visualize. The database is seeded from a CSV file representing an **anonymized** version of a real tracker scan received from a third-party provider (TrustArc).

The file *'DevOps - Homework-1 - Angela Madjar.pdf'* documents the process of containerizing this application using Docker and addresses all or the homework requirements.

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


## How to run

### Step 1. Get the image (pull or build)
- Pull the image from my public Docker Hub repository
```bash 
docker pull madjarangela/devops-homework-1:devops-homework1
```

- Or build the image from the Dockerfile (from backend/)

```bash 
docker build -t cookiejar-api:1.1 -f dockerfile .
```

### Step 2. Run a self-sufficient container (with SQLite inside it)
```bash 
docker run --rm -p 8080:8080 \
  -e DATABASE_URL="sqlite:////tmp/test.db" \
  madjarangela/devops-homework-1:devops-homework1 
```
or
```bash
docker run --rm -p 8080:8080 \
  -e DATABASE_URL="sqlite:////tmp/test.db" \
  cookiejar-api:1.1
```
Verify and use the UI by opening **http://localhost:8080/trackers** in your browser.

### Step 3. Two-container setup (App and DB)
- Create network and volume
```bash
docker network create cookiejar-net
docker volume create cookiejar_pgdata
```

- Run PostgreSQL container
```bash
docker run -d --name cookiejar-db --network cookiejar-net \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=postgres \
  -v cookiejar_pgdata:/var/lib/postgresql/data \
  postgres:16-alpine
```

- Run application container connected to PostgreSQL (depending whether you've pulled it from DockerHub or built it from Dockerfile)
```bash
docker run --rm --name cookiejar-api --network cookiejar-net \
  -p 8080:8080 \
  -e DATABASE_URL="postgresql+psycopg2://postgres:postgres@cookiejar-db:5432/postgres" \
  madjarangela/devops-homework-1:devops-homework1
```

```bash
docker run --rm --name cookiejar-api --network cookiejar-net \
  -p 8080:8080 \
  -e DATABASE_URL="postgresql+psycopg2://postgres:postgres@cookiejar-db:5432/postgres" \
  cookiejar-api:1.1
```

- Verify and use the UI by opening **http://localhost:8080/trackers** in your browser.

### Step 4: Clean up
```bash
docker stop cookiejar-api cookiejar-db
docker network rm cookiejar-net
docker volume rm cookiejar_pgdata
docker rmi cookiejar-api:1.1
docker rmi madjarangela/devops-homework-1:devops-homework1
docker rmi postgres:16-alpine
```