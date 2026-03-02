FROM python:3.12-slim
WORKDIR /app
RUN pip install pycryptodome flask
COPY app.py init_crypto.py /app/
RUN echo "LEVELUP{A_jmEHJLteTd4S7yqreOq1owqlH9Coc7}" > /flag.txt && chmod 0400 /flag.txt \
    && python3 init_crypto.py \
    && rm /flag.txt init_crypto.py
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app
USER ctfuser
EXPOSE 5000
CMD ["python", "app.py"]