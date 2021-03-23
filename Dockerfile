FROM python:3.8

WORKDIR /usr/src/app

COPY main.py .
COPY requirements.txt .

#RUN apk add --update --no-cache   g++ gcc libxslt-dev
RUN pip install --no-cache-dir -r requirements.txt

#EXPOSE 443

CMD ["python", "./main.py"]
