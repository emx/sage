FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Initialize the database and flag
RUN echo "LEVELUP{m898IfjDBxEg9Ht19ih0YufdlbGv7ben}" > /flag.txt && \
    chmod 0400 /flag.txt && \
    python init_db.py && \
    rm -f /flag.txt

RUN rm -f Dockerfile

RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]