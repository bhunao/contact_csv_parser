FROM python:3.11-slim-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /web

COPY requirements.in .

RUN apt-get update && apt-get install -y \
    && pip install --upgrade pip \
    && pip install pip-tools==7.4.1

RUN pip-compile requirements.in > requirements.txt
RUN pip install -r requirements.txt

EXPOSE 8777

COPY . /web

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8777", "--reload"]
