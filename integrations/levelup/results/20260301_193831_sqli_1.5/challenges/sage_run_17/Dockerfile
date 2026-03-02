FROM python:3.12-slim

WORKDIR /app

RUN pip install flask

COPY . .

# Secure the flag
RUN echo "LEVELUP{3Gg4vBxTRlhQoYike2RS3vmA3eweKbLn}" > /flag.txt && chmod 0400 /flag.txt

# Initialize the database
RUN python init_db.py

# Cleanup and user setup
RUN rm -f Dockerfile
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]