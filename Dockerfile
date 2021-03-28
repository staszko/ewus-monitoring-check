FROM python:3.8-alpine

LABEL maintainer="https://github.com/staszko"
LABEL version="0.1"
LABEL description="Docker image of nagions/icinga ewus check"

WORKDIR /usr/src/app

COPY main.py requirements.txt ./

RUN  set -eux; \
     apk add --update --no-cache  --virtual .build-deps  g++ gcc libxslt-dev && \
     apk add --no-cache libxslt && \
     pip install --no-cache-dir -r requirements.txt && \
     apk del .build-deps

CMD ["python", "./main.py"]
