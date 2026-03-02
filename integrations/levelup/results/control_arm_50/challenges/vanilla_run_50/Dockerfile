FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Initialize database as root to read /flag.txt
RUN echo "LEVELUP{SGWCobVfHAbnBmIFkOH4sdxJQCG0W1pZ}" > /flag.txt && chmod 0400 /flag.txt
RUN python init_db.py
RUN rm -f /flag.txt

RUN rm -f Dockerfile

RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]