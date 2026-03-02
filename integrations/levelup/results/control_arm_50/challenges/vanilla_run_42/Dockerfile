FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir flask

# Set up flag and database
RUN echo "LEVELUP{6rekj5y0SQWwbCE7B0Q7R8gnj265eMcw}" > /flag.txt && chmod 0400 /flag.txt
RUN python init_db.py
RUN rm -f /flag.txt Dockerfile

# Security hardening
RUN useradd -m ctfuser
RUN chown -R root:root /app && chmod -R 755 /app
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]