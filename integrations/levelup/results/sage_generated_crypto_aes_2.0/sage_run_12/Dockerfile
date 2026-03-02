FROM python:3.12-slim
WORKDIR /app
RUN pip install pycryptodome flask
COPY app.py init_crypto.py crypto_utils.py ./
RUN echo "LEVELUP{VcLXEygNhsw7TeoUklda4hbalFu9vtnG}" > /flag.txt && \
    python3 init_crypto.py && \
    rm /flag.txt init_crypto.py && \
    useradd -m ctfuser && \
    chown -R ctfuser:ctfuser /app
USER ctfuser
EXPOSE 5000
CMD ["python", "app.py"]