FROM python:3.7.13-alpine3.15

WORKDIR /app

RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev \
    && apk add libffi-dev
RUN python3 -m pip install --upgrade pip

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

COPY --from=trufflesecurity/trufflehog:3.6.9 /usr/bin/trufflehog /usr/bin/trufflehog

CMD [ "python3", "main.py"]