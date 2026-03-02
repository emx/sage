FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask

# Secure the flag as per requirements
RUN echo "LEVELUP{naobiUUyRFc9fhWtOVmZuMQSx1cPkvWw}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database and clean up sensitive build artifacts
RUN python init_db.py && rm -f Dockerfile /flag.txt

# Security: non-root user
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /tmp
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]