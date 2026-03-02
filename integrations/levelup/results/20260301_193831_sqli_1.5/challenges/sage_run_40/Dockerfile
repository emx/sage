FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Flag isolation: Read-only for root, app runs as non-root
RUN echo "LEVELUP{_8fbHcYfYmCi2TXDkrJ6B4tLDG3XrKE_}" > /flag.txt && chmod 0400 /flag.txt

# Initialize DB in /tmp (writable at runtime) 
RUN python init_db.py && rm -f Dockerfile

RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app /tmp
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]