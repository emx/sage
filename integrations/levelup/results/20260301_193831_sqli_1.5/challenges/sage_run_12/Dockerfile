FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Create the flag file and set permissions
RUN echo "LEVELUP{ULWgNzhnPj1Ede04ZZhKM_Y4Zu4QyIBK}" > /flag.txt && chmod 0400 /flag.txt

# Initialize the database during build
RUN python init_db.py

# Secure the environment
RUN rm -f Dockerfile init_db.py
RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]