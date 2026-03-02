FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Secure the flag
RUN echo "LEVELUP{4IeoVHLBxRVAiWEazAyMj9LfBaHyez5p}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database - this runs as root so it can read /flag.txt
RUN python init_db.py && rm /flag.txt

# Remove Dockerfile from the image
RUN rm -f Dockerfile

# Set up non-root user
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]