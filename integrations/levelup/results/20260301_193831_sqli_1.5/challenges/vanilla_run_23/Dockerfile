FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask

# Secure the flag
RUN echo "LEVELUP{AvVxD12JjvzZQXbo8ZeZVJipKziOJcoK}" > /flag.txt && \
    chmod 0400 /flag.txt

# Initialize the database during build
RUN python init_db.py

# Cleanup and user setup
RUN rm -f Dockerfile /flag.txt
RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]