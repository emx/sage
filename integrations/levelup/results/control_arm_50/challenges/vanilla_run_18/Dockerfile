FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask

RUN echo "LEVELUP{2L973lCa5GNI5tilDACs25hJj9pA7tAl}" > /flag.txt && chmod 0400 /flag.txt

# Run initialization as root to read /flag.txt
RUN python init_db.py

RUN rm -f Dockerfile /flag.txt

RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]