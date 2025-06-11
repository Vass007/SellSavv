FROM python:3.11

WORKDIR /app

COPY requirements.txt /app/
RUN apt-get update && apt-get install -y build-essential && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . /app/

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]