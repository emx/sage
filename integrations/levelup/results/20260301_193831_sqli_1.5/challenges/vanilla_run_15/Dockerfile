FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir flask

# Copy application files
COPY . .

# Create the flag file and set permissions
RUN echo "LEVELUP{PpKzROxhRy1ZKMVCYqjKhslg9tF58K8n}" > /flag.txt && chmod 0400 /flag.txt

# Initialize the database (this reads /flag.txt and stores it in the DB)
RUN python init_db.py

# Remove Dockerfile to prevent flag leakage
RUN rm -f Dockerfile

# Ensure the database is moved to a writable location at runtime
# and create a non-root user
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app

USER ctfuser

EXPOSE 5000

# At runtime, we copy the seed DB to /tmp so it remains writable for the session
CMD ["sh", "-c", "cp /app/astravantage.db /tmp/astravantage.db && python app.py"]