FROM python:3.12-slim

WORKDIR /app

COPY . .
RUN rm -f Dockerfile

RUN pip install flask

# Initialize database in /tmp and set permissions
RUN python init_db.py && \
    echo "LEVELUP{F55_Z30cPFeQJlT5a0N1fvcHrYlESMdT}" > /flag.txt && \
    # Flag is read by init_db.py during build, now we remove the source
    rm -f /flag.txt && \
    rm -f Dockerfile

RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app /tmp

USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]