FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Create flag and set permissions
RUN echo "LEVELUP{4U4ZvA0TNTq8Ud2vOJ8fj2TPaAyJw5NK}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database (runs as root to read /flag.txt)
RUN python init_db.py

# Secure the environment
RUN rm -f Dockerfile /flag.txt init_db.py

# Create non-root user
RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]