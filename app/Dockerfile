FROM python:3.12.6-slim
RUN apt-get update && apt-get install -y pip
RUN pip install flask pandas scikit-learn
RUN mkdir -p /app
WORKDIR /app
COPY app.py /app/app.py
COPY templates /app/templates
COPY static /app/static
RUN chmod +x /app/app.py
CMD ["python", "/app/app.py"]