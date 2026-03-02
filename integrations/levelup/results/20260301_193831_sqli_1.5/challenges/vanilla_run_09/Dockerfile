FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y sqlite3 && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir flask

# Secure the flag
RUN echo "LEVELUP{FEJqASexVzvtoezNVX4M76feoMLfZkd2}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database as root to allow reading /flag.txt
RUN python init_db.py

# Cleanup and user setup
RUN rm -f Dockerfile
RUN useradd -m ctfuser
RUN chown -R ctfuser:ctfuser /app
RUN chown ctfuser:ctfuser /tmp/thalassa.db

USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]