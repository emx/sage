FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask

# Secure flag placement
RUN echo "LEVELUP{sU_ijPvPSf1nmSWfUENeyEtM_fO8P8G9}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database (reads /flag.txt as root)
RUN python init_db.py

# Clean up and user safety
RUN rm -f Dockerfile /flag.txt
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app /tmp

USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]