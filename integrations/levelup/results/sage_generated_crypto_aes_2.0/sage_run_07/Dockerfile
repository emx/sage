FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN echo "LEVELUP{kQKiNFzDQ1pCAvVG1TvChtdPSWoyjpSK}" > /flag.txt && chmod 0400 /flag.txt

# init_crypto.py runs as root to read /flag.txt, encrypt it, and store results
RUN python3 init_crypto.py

# Ensure the app and keys are owned by root, but key is readable by ctfuser for the app to function
RUN chmod 0444 /app/challenge_data.json && chmod 0444 /app/secret.key

RUN rm -f Dockerfile

RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python3", "app.py"]