FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Secure the flag
RUN echo "LEVELUP{5tHng1hTrmMDQBHCn3AzJkEUtELIuF4v}" > /flag.txt && \
    chmod 0400 /flag.txt

# Initialize database and move it to a safe location
# init_db.py will read /flag.txt and create /app/vesper.db
RUN python init_db.py

# Remove sensitive files after initialization
RUN rm -f Dockerfile /flag.txt init_db.py

# Create non-root user
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]