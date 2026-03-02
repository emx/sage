FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Flag isolation: Create flag file with root-only permissions
RUN echo "LEVELUP{midw2_ldNWEebMu85ru9ukB6HNQkGYFs}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database (runs as root to read /flag.txt)
RUN python init_db.py

# Clean up sensitive build files
RUN rm -f Dockerfile init_db.py /flag.txt

# Security: Run as non-root user
RUN useradd -m ctfuser
RUN chown -R ctfuser:ctfuser /app
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]