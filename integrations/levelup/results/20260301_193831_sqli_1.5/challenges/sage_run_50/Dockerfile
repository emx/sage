FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir flask

# Flag isolation: Create flag.txt and set permissions
RUN echo "LEVELUP{fRjTh4cws5zQ8HOoM0lRSp20IU733IS7}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database and remove Dockerfile
RUN python init_db.py && rm -f Dockerfile

# Use non-root user
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app /tmp
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]