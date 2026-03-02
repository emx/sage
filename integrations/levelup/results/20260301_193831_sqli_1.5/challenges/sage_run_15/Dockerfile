FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Initialize database and flag
RUN echo "LEVELUP{a5Skwf7h3BZheElaNchfhy_45YedcAIc}" > /flag.txt && \
    chmod 0400 /flag.txt && \
    python init_db.py && \
    rm -f /flag.txt

RUN rm -f Dockerfile

RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]