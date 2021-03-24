FROM python:3.8-alpine

WORKDIR /usr/src/app

COPY main.py .
COPY requirements.txt .

RUN apk add --update --no-cache  --virtual .build-deps  g++ gcc libxslt-dev && \
     apk add --no-cache libxslt && \
     pip install --no-cache-dir -r requirements.txt && \
     apk del .build-deps

#EXPOSE 443

CMD ["python", "./main.py"]
