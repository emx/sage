FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create app directory
WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir flask

# Copy application files
COPY . .

# Flag setup: write flag and set permissions
RUN echo "LEVELUP{gGyK11JDuRPff6t278M8LJU6hqSbglfp}" > /flag.txt && chmod 0400 /flag.txt

# Initialize the database during build (runs as root, can read /flag.txt)
RUN python init_db.py

# Security: Remove Dockerfile from the container
RUN rm -f Dockerfile

# Set up non-root user
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app
USER ctfuser

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]