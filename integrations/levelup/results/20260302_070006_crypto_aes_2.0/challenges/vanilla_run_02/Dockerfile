FROM python:3.12-slim
WORKDIR /app
RUN pip install pycryptodome flask
COPY app.py crypto_utils.py init_crypto.py ./ 
RUN echo "LEVELUP{USuEvQGvQczcS7YPjgRdTl7HWJ1NB9JI}" > /flag.txt && chmod 0400 /flag.txt \
    && python3 init_crypto.py \
    && rm /flag.txt init_crypto.py
RUN useradd -m ctfuser
USER ctfuser
EXPOSE 5000
CMD ["python", "app.py"]