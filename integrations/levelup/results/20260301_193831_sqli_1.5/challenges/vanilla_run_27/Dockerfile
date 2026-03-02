FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Secure the flag
RUN echo "LEVELUP{GcvMUE5PiGLsRtRAMJ_XUpasFddVyaGB}" > /flag.txt && chmod 0400 /flag.txt

# Initialize the database during build as root (to read /flag.txt)
# The DB is created in /app first, then moved/managed by the app
RUN python init_db.py && rm -f /flag.txt

# Remove Dockerfile to prevent players from reading build steps
RUN rm -f Dockerfile

# Create non-root user
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]