# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# If I wasn't using the psycopg2-binary package, I would have needed 
# to install the following dependencies for the driver allowing Python to talk to PostgreSQL
# gcc - C compailer; libpd-vev - Postgres client dev libraries
# RUN apt-get update \
#     && apt-get install -y --no-install-recommends gcc libpq-dev \
#     && rm -rf /var/lib/apt/lists/*

# Compy and Install the required packages
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Expose the port that the Flask app will run on
EXPOSE 8080

# Run the app
CMD ["gunicorn", "-b", ":8080", "--timeout", "0", "app:app"]
