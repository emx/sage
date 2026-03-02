FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask

# Secure the flag
RUN echo "LEVELUP{qdja5wTxKreTxdMMlhtVUotEIS6Ax6bd}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database as root to read /flag.txt
RUN python init_db.py

# Clean up
RUN rm -f Dockerfile /flag.txt

# Non-root user setup
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /tmp
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]