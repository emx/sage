FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask

# Secure flag handling
RUN echo "LEVELUP{_OAT24n03kyolmG5IdsazsZYDFmQor54}" > /flag.txt && chmod 0400 /flag.txt

# Initialize database (creates /tmp/stratosvane.db)
RUN python init_db.py

# Remove flag source and Dockerfile from final image
RUN rm -f /flag.txt Dockerfile

# Set up non-root user
RUN useradd -m ctfuser && chown -R ctfuser:ctfuser /app
USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]