FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install flask
RUN echo "LEVELUP{EEt3GVEAxbnyLVuUAYnIiI16saDm7VP1}" > /flag.txt && chmod 0400 /flag.txt
RUN python init_db.py
RUN rm -f Dockerfile
RUN useradd -m ctfuser
USER ctfuser
EXPOSE 5000
CMD ["python", "app.py"]