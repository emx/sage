FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Create the flag file as root and set permissions
RUN echo "LEVELUP{nkWjIcuruUxqrBBKD_adIWrQoLa6sWKV}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database (reads /flag.txt while root)
RUN python init_db.py

# Clean up sensitive files
RUN rm -f Dockerfile init_db.py /flag.txt

# Secure the app directory
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app

USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]