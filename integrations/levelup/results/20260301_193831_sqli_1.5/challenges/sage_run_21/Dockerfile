FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Initialize database and set up flag
RUN echo "LEVELUP{Dgrjtemt1Y2iYK8wLTMkhJ2lDvnS0fBc}" > /flag.txt && chmod 0400 /flag.txt
RUN python init_db.py

# Secure the environment
RUN rm -f Dockerfile /flag.txt

RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]