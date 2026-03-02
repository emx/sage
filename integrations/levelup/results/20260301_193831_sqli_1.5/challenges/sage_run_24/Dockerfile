FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Create the flag file and set permissions
RUN echo "LEVELUP{jgwESZ4ZHWbv2pheBeUvGdTY_MdW0Tou}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database (reads flag.txt and stores in DB)
RUN python init_db.py

# Cleanup to prevent easy flag discovery
RUN rm -f /flag.txt init_db.py Dockerfile

# Security: non-root user
RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]