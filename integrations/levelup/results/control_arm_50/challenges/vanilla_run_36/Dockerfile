FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir Flask

# Copy application files
COPY . .

# Create flag file and set permissions
RUN echo "LEVELUP{ONkOFu18zDZAZ78d8t7WJVyS8jMaFo0Q}" > /flag.txt && \
    chmod 0400 /flag.txt

# Initialize the database (as root to read /flag.txt)
RUN python init_db.py

# Secure the environment
RUN rm -f Dockerfile /flag.txt

# Create non-root user
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app /tmp
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]