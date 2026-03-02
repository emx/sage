FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Secure the flag
RUN echo "LEVELUP{xIsYj0hsNRnQpfzdTNmt7WXM4rEUo2XR}" > /flag.txt && chmod 0400 /flag.txt

# Initialize the database (this runs as root, can read /flag.txt)
RUN python init_db.py

# Cleanup and non-root user setup
RUN rm -f Dockerfile
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app

# Only /tmp is writable at runtime
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]