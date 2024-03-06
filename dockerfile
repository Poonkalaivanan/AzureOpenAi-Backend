FROM python:3.9-slim
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD gunicorn -b 0.0.0.0:8080 -t 10 --timeout 90 -w 2 main:app debug=True