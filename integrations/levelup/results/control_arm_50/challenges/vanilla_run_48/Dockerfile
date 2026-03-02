FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Flag isolation: written by root, mode 0400
RUN echo "LEVELUP{MzCpdcaaAfxs22pTpB6LXnxAi_jgCKpA}" > /flag.txt && chmod 0400 /flag.txt

# Initialize DB in /tmp (writable at runtime)
RUN python init_db.py

# Clean up sensitive files
RUN rm -f Dockerfile init_db.py /flag.txt

# Create non-root user
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]