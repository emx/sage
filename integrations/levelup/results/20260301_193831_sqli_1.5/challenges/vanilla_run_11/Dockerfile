FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Create the flag file and set permissions
RUN echo "LEVELUP{4klwJvGuZP6xDWFtzYJXpAMKfUUmBrZs}" > /flag.txt && chmod 0400 /flag.txt

# Initialize the database (this runs as root and can read /flag.txt)
RUN python init_db.py

# Remove the Dockerfile to prevent players from reading it
RUN rm -f Dockerfile

# Secure the database file - move it to /app/ and set ownership
RUN chown root:root /app/aetherflow_template.db && chmod 0644 /app/aetherflow_template.db

# Create a non-root user
RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

# Copy DB to /tmp at runtime to allow SQLite to handle journaling on a read-only FS
CMD ["sh", "-c", "cp /app/aetherflow_template.db /tmp/aetherflow.db && python app.py"]