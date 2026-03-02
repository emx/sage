FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Secure the flag
RUN echo "LEVELUP{aFafeD5yqyBE4G67xQDBkvRylu3TjkJ_}" > /flag.txt && \
    chmod 0400 /flag.txt

# Initialize DB as root (can read /flag.txt)
RUN python init_db.py

# Cleanup and user setup
RUN rm -f Dockerfile init_db.py
RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]