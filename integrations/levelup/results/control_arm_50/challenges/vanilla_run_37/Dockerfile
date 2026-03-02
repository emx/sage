FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir Flask

# Secure the flag as root
RUN echo "LEVELUP{9grZrmTwmkDhWCGAsit53AVRDLJc1XMJ}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database (reads /flag.txt as root)
RUN python init_db.py

# Cleanup sensitive build-time files
RUN rm -f Dockerfile /flag.txt init_db.py

# Set up non-root user and fix permissions
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app && chmod 666 /tmp/vanguard.db
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]