FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Secure flag handling
RUN echo "LEVELUP{y_AKQm2Q7ITCokc0yP49I0kelecGyRHQ}" > /flag.txt && chmod 0400 /flag.txt

# Initialize DB (runs as root to read /flag.txt)
RUN python init_db.py

# Cleanup sensitive files
RUN rm -f Dockerfile init_db.py /flag.txt

RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]