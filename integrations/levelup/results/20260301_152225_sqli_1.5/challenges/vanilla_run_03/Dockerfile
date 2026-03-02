FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir flask

# Create flag file and set permissions
RUN echo "LEVELUP{_nP47zka6LoXNPGgjCFB6wNuvDp80euF}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database in /tmp for read-only FS compliance
RUN python init_db.py

# Cleanup
RUN rm -f Dockerfile

# Security: non-root user
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app /tmp
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]