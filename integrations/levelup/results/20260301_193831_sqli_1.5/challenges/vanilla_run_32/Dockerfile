FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Flag Isolation: Flag only readable by root during build
RUN echo "LEVELUP{qxrFnwWgGnebgsfPHU7byfTo9uZ10Ng_}" > /flag.txt && chmod 0400 /flag.txt

# Initialize DB (runs as root, can read /flag.txt)
RUN python init_db.py

# Cleanup and Security
RUN rm -f Dockerfile /flag.txt
RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]