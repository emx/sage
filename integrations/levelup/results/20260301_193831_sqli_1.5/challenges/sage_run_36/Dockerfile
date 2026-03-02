FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask

# Secure flag placement and DB initialization
RUN echo "LEVELUP{0pdpvfUtsymxf7BOmNJOiBcoUoLebESu}" > /flag.txt && chmod 0400 /flag.txt
RUN python init_db.py
RUN rm -f /flag.txt
RUN rm -f Dockerfile

RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app /tmp
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]