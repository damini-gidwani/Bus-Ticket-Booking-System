FROM python:3.12

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["streamlit","run","bus.py","--server.port=8501","--server.address=0.0.0.0"]
