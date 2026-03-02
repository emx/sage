FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Flag Isolation: Flag is 0400 and owned by root. Only init_db.py (running as root) can read it.
RUN echo "LEVELUP{OSvjVW6g0e88Oh4SX_gbwYygKhjmudzE}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database in /tmp for read-only filesystem compatibility
RUN python init_db.py

# Clean up and switch to non-root user
RUN rm -f Dockerfile
RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]