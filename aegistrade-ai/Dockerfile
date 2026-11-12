FROM python:3.11-slim
WORKDIR /app
COPY requirements-full.txt requirements-neural.txt requirements-market.txt ./
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements-full.txt
COPY . .
ENV PYTHONPATH=/app
ENV AEGIS_DATA_DIR=/app/data
RUN mkdir -p /app/data
CMD ["uvicorn","app.api:app","--host","0.0.0.0","--port","8000"]
