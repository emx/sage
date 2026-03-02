FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask

# Flag Isolation: Write flag to root-only file
RUN echo "LEVELUP{L7Ij4XzhVyjCV6CNAYg5iWHKhRd9f7mI}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database (reads /flag.txt as root during build)
RUN python init_db.py

# Cleanup and security
RUN rm -f Dockerfile init_db.py /flag.txt
RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]