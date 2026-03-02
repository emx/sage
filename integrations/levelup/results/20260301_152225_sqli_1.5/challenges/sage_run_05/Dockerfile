FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask

# Secure the flag
RUN echo "LEVELUP{mYvKrq3Mwob95Y1LQ4kq33XONt73fjg8}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database (reads /flag.txt as root)
RUN python init_db.py

# Clean up sensitive build files
RUN rm -f Dockerfile /flag.txt

# Production hardening
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app /tmp
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]