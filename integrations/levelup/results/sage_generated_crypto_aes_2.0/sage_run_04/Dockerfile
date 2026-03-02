FROM python:3.12-slim
WORKDIR /app
RUN pip install pycryptodome flask
COPY app.py init_crypto.py ./
RUN echo "LEVELUP{57d3NIKTkaSCZ1nC3QTAPKoYa50NbFQ0}" > /flag.txt && chmod 0400 /flag.txt \
    && python3 init_crypto.py \
    && rm /flag.txt init_crypto.py
RUN useradd -m ctfuser
USER ctfuser
EXPOSE 5000
CMD ["python", "app.py"]