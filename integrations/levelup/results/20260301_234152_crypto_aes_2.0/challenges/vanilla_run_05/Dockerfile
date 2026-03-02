FROM python:3.12-slim

RUN apt-get update && apt-get install -y binutils && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir flask pycryptodome

COPY . .

RUN echo "LEVELUP{ffLwrk7vyWZi23dg4WcbNOXwDxaW5R9T}" > /flag.txt && chmod 0400 /flag.txt

RUN python3 init_crypto.py && rm -f /flag.txt

RUN chown root:root /app && chmod 755 /app
RUN chmod 0444 /app/challenge_data.json

RUN rm -f Dockerfile

RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000

CMD ["python3", "app.py"]