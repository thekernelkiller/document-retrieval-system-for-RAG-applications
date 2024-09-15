FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

ENV FLASK_APP=app.main

CMD ["streamlit", "run", "app/streamlit_app.py"]