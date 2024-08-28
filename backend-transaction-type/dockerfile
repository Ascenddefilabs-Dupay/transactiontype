FROM python:3.11-slim

WORKDIR /backend-transaction-type

COPY requirements.txt /backend-transaction-type/
RUN pip3 install -r /backend-transaction-type/requirements.txt

COPY . .


CMD ["python", "manage.py", "runserver", "0.0.0.0:8004"]
