FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Create flag and set permissions
RUN echo "LEVELUP{9HHhEJPyldj_582z6H1h2qwLeQiw_MS6}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database - this runs as root to read /flag.txt
RUN python init_db.py

# Cleanup sensitive files and set up non-root user
RUN rm -f /flag.txt Dockerfile init_db.py
RUN useradd -m ctfuser
RUN chown -R root:root /app && chmod -R 755 /app
# Ensure the database is writable by ctfuser (required for SQLite in /tmp)
RUN chown ctfuser:ctfuser /tmp

USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]