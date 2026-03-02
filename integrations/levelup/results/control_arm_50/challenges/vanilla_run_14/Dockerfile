FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Initialize database in /tmp as per read-only requirements
# Root permission is needed to read /flag.txt during initialization
RUN echo "LEVELUP{NmGr_2x8F5SM0cJDYJLLN3D5Wz6toLEK}" > /flag.txt && chmod 0400 /flag.txt
RUN python init_db.py

RUN rm -f Dockerfile

# Secure the flag file after DB initialization
RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]