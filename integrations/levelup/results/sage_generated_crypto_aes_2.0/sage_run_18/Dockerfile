FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir flask pycryptodome

COPY . .

RUN echo "LEVELUP{2Y1FK0dTufQxI0FsK6FkrS_cJrGr9jLg}" > /flag.txt && chmod 0400 /flag.txt

RUN python3 init_crypto.py

RUN rm -f Dockerfile init_crypto.py /flag.txt

RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app

USER ctfuser

EXPOSE 5000

CMD ["python3", "app.py"]