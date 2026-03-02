FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Create the flag file as root
RUN echo "LEVELUP{UJtIQ0CbEkP8JTtOovDSKfJa7O1AceIs}" > /flag.txt && chmod 0400 /flag.txt

# Initialize the database (this will read /flag.txt and create /app/velosync.db)
RUN python init_db.py

# Secure the environment
RUN rm -f Dockerfile init_db.py /flag.txt

# Ensure the database is writable by ctfuser (SQLite needs to write journal files)
RUN useradd -m ctfuser && chown ctfuser:ctfuser /app && chown ctfuser:ctfuser /app/velosync.db

USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]