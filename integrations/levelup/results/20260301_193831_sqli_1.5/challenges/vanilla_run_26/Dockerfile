FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Secure flag placement
RUN echo "LEVELUP{AVQfA8tY43s7IZAvSDRq9M85puKBDQQp}" > /flag.txt && chmod 0400 /flag.txt

# Initialize DB and clean up
RUN python init_db.py
RUN rm -f Dockerfile /flag.txt

# Setup non-root user
RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]