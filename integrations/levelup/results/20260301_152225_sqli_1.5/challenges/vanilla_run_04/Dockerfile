FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Initialize DB in /app first, then it will be moved to /tmp at runtime
# Flag setup: Create flag file with root-only permissions
RUN echo "LEVELUP{zFjdBYc_fcUhidLGJncdppiC77LC6QqP}" > /flag.txt && chmod 0400 /flag.txt

# Run initialization as root to read /flag.txt
RUN python init_db.py

# Cleanup
RUN rm -f Dockerfile init_db.py /flag.txt

RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]