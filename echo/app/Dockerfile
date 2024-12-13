FROM python:3.12.6-slim
RUN apt-get update && apt-get install -y
RUN pip install flask
WORKDIR /app
COPY app.py /app/
CMD ["python", "app.py"]