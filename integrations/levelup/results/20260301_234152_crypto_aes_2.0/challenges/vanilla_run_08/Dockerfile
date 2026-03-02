FROM python:3.12-slim
WORKDIR /app
RUN pip install pycryptodome flask
COPY app.py init_crypto.py ./
RUN echo "LEVELUP{vdz_hzH319_T7hsjroyFzyrVysJJBxru}" > /flag.txt && chmod 0400 /flag.txt \
    && python3 init_crypto.py \
    && chmod 0644 challenge_data.json \
    && rm /flag.txt init_crypto.py
RUN useradd -m ctfuser
USER ctfuser
EXPOSE 5000
CMD ["python", "app.py"]