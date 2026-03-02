FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask

# Secure the flag
RUN echo "LEVELUP{miqJxXKb3cpjGG6Hnl6RP6aCfroWXNJq}" > /flag.txt && chmod 0400 /flag.txt

# Initialize the database as root (to read /flag.txt)
RUN python init_db.py

# Cleanup and user setup
RUN rm -f Dockerfile
RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]