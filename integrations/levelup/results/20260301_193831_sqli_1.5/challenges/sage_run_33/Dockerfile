FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask

RUN echo "LEVELUP{wzA2sDAcI9n13uaJ9GTmqAjwUMKbFFmm}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database and move to /tmp for read-only filesystem support
RUN python init_db.py

RUN rm -f Dockerfile init_db.py

RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app

# Ensure the DB is in /tmp for runtime write access
RUN mv /app/veridian.db /tmp/veridian.db && chown ctfuser:ctfuser /tmp/veridian.db

USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]