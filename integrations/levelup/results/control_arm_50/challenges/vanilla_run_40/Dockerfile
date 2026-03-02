FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Create the flag file and set permissions
RUN echo "LEVELUP{b4zGRr71E6ksI9kZhouHcKZNY5AHO5QT}" > /flag.txt && chmod 0400 /flag.txt

# Initialize the database - it reads /flag.txt as root
RUN python init_db.py

# Clean up the sensitive Dockerfile
RUN rm -f Dockerfile

# Secure environment
RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]