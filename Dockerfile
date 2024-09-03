FROM python:3.9-slim

USER root

COPY requirements.txt /tmp/requirements.txt

RUN pip3 install -r /tmp/requirements.txt

WORKDIR /app

COPY main.py /app/main.py
COPY forms.py /app/forms.py
COPY gpt_api_class.py /app/gpt_api_class.py
COPY templates /app/templates

CMD ["python3", "main.py"]
