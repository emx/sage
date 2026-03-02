FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Secure the flag
RUN echo "LEVELUP{2QzwgVJIdDOZiOgEE0IIqlYwbySvCqTe}" > /flag.txt && chmod 0400 /flag.txt

# Initialize DB (as root to read /flag.txt)
RUN python init_db.py

# Cleanup and Permissions
RUN rm -f Dockerfile
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]