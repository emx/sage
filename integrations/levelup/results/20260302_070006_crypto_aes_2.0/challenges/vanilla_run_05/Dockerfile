FROM python:3.12-slim
WORKDIR /app
RUN pip install pycryptodome flask
COPY app.py crypto_utils.py init_crypto.py ./
RUN echo "LEVELUP{DKmJMobvcekZUt0kpFR38i00Uugh9Vim}" > /flag.txt && \
    chmod 0400 /flag.txt && \
    python3 init_crypto.py && \
    rm /flag.txt init_crypto.py
RUN useradd -m ctfuser
USER ctfuser
EXPOSE 5000
CMD ["python", "app.py"]