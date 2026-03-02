FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask

# Secure the flag
RUN echo "LEVELUP{nm20MIBCcdrKYRpvjPWYz3wWIMswOdU3}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database as root (to read /flag.txt)
RUN python init_db.py

# Clean up sensitive build files
RUN rm -f Dockerfile /flag.txt init_db.py

# Use a non-root user
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app /tmp
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]