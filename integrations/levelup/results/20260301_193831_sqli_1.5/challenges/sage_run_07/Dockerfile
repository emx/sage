FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Flag isolation: Create flag.txt and restrict access
RUN echo "LEVELUP{hj2WKHuMqWnIhI9Lq5Y9tcjmhOrLCR7w}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database in /tmp for read-only filesystem compatibility
RUN python init_db.py

RUN rm -f Dockerfile

# Run as non-root user
RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]