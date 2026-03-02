FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask

# Flag setup: write to /flag.txt, only root can read
RUN echo "LEVELUP{QP6f8SC0yWzLpjRE0jBfuUHDBmQyydIg}" > /flag.txt && chmod 0400 /flag.txt

# Initialize DB (runs as root to read /flag.txt)
RUN python init_db.py

# Clean up
RUN rm -f /flag.txt Dockerfile init_db.py

# Non-root user setup
RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]