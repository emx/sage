FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Initialize the database during build (runs as root)
RUN python init_db.py

# Secure the flag file
RUN echo "LEVELUP{I5keCaxxcYt4cydK_AMQMLkXGL1u_vnr}" > /flag.txt && chmod 0400 /flag.txt

# Clean up and set permissions
RUN rm -f Dockerfile
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app

# Ensure the database in /tmp is accessible
RUN chmod 666 /tmp/aetherlink.db

USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]