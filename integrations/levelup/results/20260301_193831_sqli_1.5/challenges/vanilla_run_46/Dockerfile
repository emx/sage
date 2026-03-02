FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask

# Secure the flag
RUN echo "LEVELUP{oEpgPPa8e2dKMaoC9miDCDhJMxY3jnR0}" > /flag.txt && chmod 0400 /flag.txt

# Initialize the database as root to read /flag.txt
RUN python init_db.py

RUN rm -f Dockerfile init_db.py

RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]