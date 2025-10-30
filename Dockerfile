FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV FLASK_APP=run:create_app
CMD ["gunicorn", "-b", "0.0.0.0:5000", "run:create_app"]