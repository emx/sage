FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask
RUN rm -f Dockerfile

# Initialize database as root to read /flag.txt
RUN echo "LEVELUP{vpWy4m4OQquVyT6LH49VBNYk30v4FHCX}" > /flag.txt && chmod 0400 /flag.txt
RUN python init_db.py
RUN rm /flag.txt

RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /tmp
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]