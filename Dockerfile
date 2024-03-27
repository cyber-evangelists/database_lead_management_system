FROM python:3.11.4

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD uvicorn server.app:app --reload --host=0.0.0.0 --port=8000