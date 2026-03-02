FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Create flag and set permissions
RUN echo "LEVELUP{7kosVeoLYCWqxUOu_x21d533AUJXOirT}" > /flag.txt && \
    chmod 0400 /flag.txt && \
    chown root:root /flag.txt

# Initialize database (creates /tmp/aetheria.db)
RUN python init_db.py

# Cleanup
RUN rm -f Dockerfile init_db.py

# Run as non-root user
RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]