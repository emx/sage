FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask

RUN echo "LEVELUP{O9b_7EAbcty6oAxy_U8tSO1MivKcwKgy}" > /flag.txt && chmod 0400 /flag.txt

RUN python init_db.py

RUN rm -f Dockerfile /flag.txt

RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]