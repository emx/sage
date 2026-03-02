FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Flag isolation: write flag to /flag.txt, only root can read
RUN echo "LEVELUP{mHDIi9YIN6eOcLzympJ0Zyk0YFonHu5H}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database - this runs as root so it can read /flag.txt
RUN python init_db.py

# Remove Dockerfile to prevent players from reading it
RUN rm -f Dockerfile

# Security: run as non-root user
RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]