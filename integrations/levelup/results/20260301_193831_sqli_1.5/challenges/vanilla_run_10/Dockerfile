FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Set up the flag
RUN echo "LEVELUP{sOBd6U7eZP1p04XoU7jasSbH3_4uC0Ot}" > /flag.txt && chmod 0400 /flag.txt

# Initialize the database as root so it can read /flag.txt
RUN python init_db.py && chmod 644 /app/voyant.db

# Cleanup
RUN rm -f Dockerfile /flag.txt

# Security: non-root user
RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]