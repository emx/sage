FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Secure the flag as per requirements
RUN echo "LEVELUP{ANDJdYuZa16NUQlU8OHCVweMTniSZ8rI}" > /flag.txt && \
    chmod 0400 /flag.txt && \
    chown root:root /flag.txt

# Initialize the database (runs as root to read /flag.txt)
RUN python init_db.py

# Cleanup and setup user
RUN rm -f Dockerfile
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app /tmp
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]