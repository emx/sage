FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir flask

# Secure the flag as requested
RUN echo "LEVELUP{O7kG_TSqcEabiWdFRR0MNrKaSQ7YDHCS}" > /flag.txt && chmod 0400 /flag.txt

# Initialize the database (this will read /flag.txt and create /app/data.db)
RUN python init_db.py

# Cleanup
RUN rm -f Dockerfile /flag.txt

# Read-only FS compatibility: app will copy data.db to /tmp at runtime
RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]