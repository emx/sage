FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Secure the flag
RUN echo "LEVELUP{iGHXeu8iVzmCWCVbrozbr20hCPcg5u9_}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database during build
RUN python init_db.py

# Cleanup
RUN rm -f Dockerfile init_db.py

RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]