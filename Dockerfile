FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

WORKDIR /code

RUN pip install --upgrade pip --trusted-host https://mirror-pypi.runflare.com --index-url https://mirror-pypi.runflare.com/simple/

COPY requirements.txt /code/
COPY requirements/ /code/requirements

RUN pip install -r requirements.txt --trusted-host https://mirror-pypi.runflare.com --index-url https://mirror-pypi.runflare.com/simple/

COPY . /code/

EXPOSE 8000
