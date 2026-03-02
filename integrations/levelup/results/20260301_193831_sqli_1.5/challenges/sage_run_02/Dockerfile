FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install flask

# Flag isolation: Create flag file with root-only permissions
RUN echo "LEVELUP{ISUrzOqpF_Oj2HDe3lk2wjnr5GqpUsN4}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database (reads /flag.txt as root)
RUN python init_db.py

# Security: Remove Dockerfile and restrict permissions
RUN rm -f Dockerfile

# Create non-root user
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app /tmp
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]