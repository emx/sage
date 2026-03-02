FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Flag isolation: Create flag file with restricted permissions
RUN echo "LEVELUP{cFgJze1llWUC2H9mo1bNBFmxQBPFGOw4}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database as root (to read /flag.txt)
RUN python init_db.py

# Clean up and set permissions
RUN rm -f Dockerfile /flag.txt

# Ensure /tmp is writable for the SQLite DB
RUN chmod 1777 /tmp

RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]