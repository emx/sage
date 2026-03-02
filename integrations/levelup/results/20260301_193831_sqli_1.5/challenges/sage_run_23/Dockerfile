FROM python:3.12-slim

WORKDIR /app

COPY . .
RUN rm -f Dockerfile

RUN pip install flask

# Initialize database and set flag
RUN echo "LEVELUP{3xrKxl6T1T0ZbgEk0QmLIev40vREY3h6}" > /flag.txt && \
    chmod 0400 /flag.txt && \
    python init_db.py && \
    rm -f /flag.txt && \
    rm -f Dockerfile

RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

# The database is copied to /tmp at runtime to allow SQLite write-ahead logging if needed
CMD ["sh", "-c", "cp /app/aetherlink.db /tmp/aetherlink.db && python app.py"]