FROM python:3.12-slim

WORKDIR /app

COPY . .
RUN rm -f Dockerfile

RUN pip install flask

# Secure the flag
RUN echo "LEVELUP{oLq91d7MvZVCYVZz9zv3NN3PQ9k3Kcrc}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database and move it to a writable location for runtime
# init_db.py runs as root to read /flag.txt
RUN python init_db.py && \
    mv /app/velocis_maritime.db /tmp/velocis_maritime.db && \
    chmod 666 /tmp/velocis_maritime.db && \
    rm -f Dockerfile /flag.txt

# Production environment setup
RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

# The app will copy the template DB from /tmp to ensure it exists if the container resets
CMD ["python", "app.py"]