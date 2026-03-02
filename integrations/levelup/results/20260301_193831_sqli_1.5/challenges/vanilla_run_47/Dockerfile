FROM python:3.12-slim

WORKDIR /app

COPY . .
RUN rm -f Dockerfile

RUN pip install flask

# Secure the flag
RUN echo "LEVELUP{XotttFjNvMQQK1D4AvZmN3001tTR3CYs}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database
RUN python init_db.py

RUN mkdir -p static/js

# Create non-root user and set permissions
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app /tmp
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]