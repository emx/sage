FROM python:3.12-slim

WORKDIR /app

COPY . .
RUN rm -f Dockerfile

RUN pip install flask

# Initialize database and flag
RUN echo "LEVELUP{i5k0uwgrL7uiWrh7NeeZzWXl5_TuFYB5}" > /flag.txt && \
    chmod 0400 /flag.txt && \
    python init_db.py && \
    rm -f Dockerfile /flag.txt

RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]