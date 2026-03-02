FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask

# Secure flag handling
RUN echo "LEVELUP{uArCeZNvLylWWQGF5S42x6r_sZ4MUZqY}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database (as root to read /flag.txt)
RUN python init_db.py

# Remove Dockerfile to prevent players from reading it via shell
RUN rm -f Dockerfile

# Security: non-root user
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app /tmp
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]