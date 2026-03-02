FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Flag isolation: created by root, readable by root only during build
RUN echo "LEVELUP{JlJe_czL8jp7EvugwsVBCU51wcziGwVL}" > /flag.txt && chmod 0400 /flag.txt

# Database initialization (runs as root to read /flag.txt)
RUN python init_db.py

# Cleanup sensitive build file
RUN rm -f Dockerfile /flag.txt

# Security: non-root user
RUN useradd -m ctfuser
RUN chown -R ctfuser:ctfuser /app /tmp
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]