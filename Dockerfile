FROM python:3.10

# ENV API_ID=
# ENV API_HASH=
# ENV BOT_TOKEN=
# ENV OWNER_ID=

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

COPY . /usr/src/app

RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python3", "main.py"]