FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Flag security: Create flag file and set permissions
RUN echo "LEVELUP{D1ccMeZZyI26iJsEeEEhs0AwXyIqGFNm}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database during build (as root to read flag)
RUN python init_db.py

# Clean up
RUN rm -f Dockerfile /flag.txt

# Create non-root user
RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]