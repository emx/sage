FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir Flask

# Secure the flag
RUN echo "LEVELUP{rSxj4MrnwjpkeXel7TJpjKLsWira67J3}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database (creates /tmp/verdant_pulse.db)
RUN python init_db.py

# Clean up
RUN rm -f Dockerfile /flag.txt init_db.py

# Non-root user
RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

ENV FLASK_APP=app.py
CMD ["python", "app.py"]