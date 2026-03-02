FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir Flask

# Copy application files
COPY . .

# Set up the flag with root permissions only
RUN echo "LEVELUP{TBPd_Mghovdu71bHIk6XDnR9YAysR2Gr}" > /flag.txt && chmod 0400 /flag.txt

# Initialize the database as root (to read /flag.txt)
RUN python init_db.py
RUN chmod 644 /app/vanguard.db

# Clean up
RUN rm -f Dockerfile init_db.py /flag.txt

# Non-root user setup
RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]