FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask

# Flag Isolation: Write flag to /flag.txt, only readable by root
RUN echo "LEVELUP{grBJU6KSwyM1JX7DTaXMx2ERckkC1loo}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database (reads /flag.txt as root)
RUN python init_db.py

# Remove Dockerfile to prevent players from reading it
RUN rm -f Dockerfile

# Set up non-root user
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app /tmp
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]