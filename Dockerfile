FROM python:3.10


WORKDIR /Horbus-test


COPY . .


RUN pip install --no-cache-dir -r requirements.txt


CMD ["python", "app.py"]
