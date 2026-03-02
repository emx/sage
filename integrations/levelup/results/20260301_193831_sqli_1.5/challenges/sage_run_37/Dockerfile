FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN echo "LEVELUP{yNqDTWELks1m09X2L_m7XWnMgIRsbB6y}" > /flag.txt && chmod 0400 /flag.txt
RUN pip install flask
RUN python init_db.py
RUN rm -f Dockerfile
RUN useradd -m ctfuser
USER ctfuser
EXPOSE 5000
CMD ["python", "app.py"]