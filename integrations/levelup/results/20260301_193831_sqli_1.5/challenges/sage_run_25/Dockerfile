FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir flask

# Flag Isolation: Create flag file with root-only permissions
RUN echo "LEVELUP{R3CtacjZOP7hY6USY9gPiHZbHbfmbbjC}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database (reads /flag.txt while root during build)
RUN python init_db.py

# Remove Dockerfile to prevent players from reading build steps
RUN rm -f Dockerfile

# Security: Run as non-root user
RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]