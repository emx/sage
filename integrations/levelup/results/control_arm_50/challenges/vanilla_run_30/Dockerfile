FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Create the flag file - only root can read it
RUN echo "LEVELUP{UEFNzZzPNUDzKoeZsFsqFd5ZbDllwJCY}" > /flag.txt && chmod 0400 /flag.txt

# Initialize the database - this runs as root during build to read /flag.txt
RUN python init_db.py

# Cleanup
RUN rm -f Dockerfile

# Security hardening
RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]