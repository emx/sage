FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask

# Secure the flag
RUN echo "LEVELUP{1UTRaA4YmWb7vaADL68hWZE7la5WBLKs}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database and cleanup
RUN python init_db.py
RUN rm -f Dockerfile init_db.py /flag.txt

RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]