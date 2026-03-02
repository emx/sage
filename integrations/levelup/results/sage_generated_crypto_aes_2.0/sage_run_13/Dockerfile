FROM python:3.12-slim
WORKDIR /app
RUN pip install pycryptodome flask
COPY app.py init_crypto.py ./
# Ensure the flag file exists for init_crypto.py
RUN echo "LEVELUP{cB_uyL4Yyrg0izHkvQSi9nxMl7KRZenT}" > /flag.txt
RUN python3 init_crypto.py && rm /flag.txt init_crypto.py
RUN useradd -m ctfuser
USER ctfuser
EXPOSE 5000
CMD ["python", "app.py"]