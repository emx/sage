FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Flag isolation: write flag as root, set restricted permissions
RUN echo "LEVELUP{k_lNR3JJ76_sOyUBcTvLtzOcYvTUMNNN}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database (runs as root to read /flag.txt)
# The DB is placed in /tmp for read-only FS compatibility
RUN python init_db.py && rm -f /flag.txt

RUN rm -f Dockerfile

# Security: run as non-root user
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app /tmp/nebula_logistics.db
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]