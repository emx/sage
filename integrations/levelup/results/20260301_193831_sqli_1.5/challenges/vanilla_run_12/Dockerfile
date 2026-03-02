FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask

# Secure the flag
RUN echo "LEVELUP{evxrvl5QnEhqePQwVfnaPiF3pj_vdUX2}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database - creates /tmp/velogreen.db
RUN python init_db.py

RUN rm -f Dockerfile

RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]