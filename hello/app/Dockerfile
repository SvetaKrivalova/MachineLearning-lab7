FROM python:3.12.6-slim
RUN apt-get update && apt-get install -y
WORKDIR /app
COPY hello.py /app/
CMD ["python", "hello.py"]