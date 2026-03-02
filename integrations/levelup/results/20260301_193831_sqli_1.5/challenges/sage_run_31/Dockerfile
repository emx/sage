FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Secure the flag
RUN echo "LEVELUP{qMjgchOSFgvIksW_QUvfRhV7JClxheAB}" > /flag.txt && chmod 0400 /flag.txt

# Initialize DB as root to read /flag.txt
RUN python init_db.py

# Cleanup
RUN rm -f Dockerfile /flag.txt

# Create non-root user
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app /tmp
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]