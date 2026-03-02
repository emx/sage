FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Secure the flag
RUN echo "LEVELUP{2f8iF2wINbBeFLa7bflimIJ7Le4Yrx6K}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database as root to read /flag.txt
RUN python init_db.py

# Cleanup
RUN rm -f Dockerfile /flag.txt

RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]