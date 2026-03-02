FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask

# Secure the flag
RUN echo "LEVELUP{ZE1JRW4tyRqePrC__S0c8LFw_4sw90fl}" > /flag.txt && chmod 0400 /flag.txt

# Initialize the database (this runs as root, so it can read /flag.txt)
RUN python init_db.py

# Clean up
RUN rm -f Dockerfile init_db.py

# Set up non-root user
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app /tmp
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]