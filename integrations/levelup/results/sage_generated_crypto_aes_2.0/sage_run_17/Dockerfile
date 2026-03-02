FROM python:3.12-slim

RUN apt-get update && apt-get install -y gcc python3-dev
RUN pip install --no-cache-dir flask pycryptodome gunicorn

WORKDIR /app
COPY . .

RUN echo "LEVELUP{CoDGUpmGWfZSsqpixd4VQIR0XTQAj8xO}" > /flag.txt && chmod 0400 /flag.txt

# Run the initialization script to encrypt the flag
RUN python3 init_crypto.py && rm init_crypto.py

# Ensure the key and data are protected but readable by the app
RUN useradd -m ctfuser
RUN chown root:ctfuser /app/challenge_data.json /app/telemetry.key && chmod 440 /app/challenge_data.json /app/telemetry.key

RUN rm -f Dockerfile

USER ctfuser
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]