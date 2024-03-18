FROM python:3.12.1

RUN pip install --upgrade pip

RUN apt update 

WORKDIR /web-market

COPY . .

RUN pip install -r requirements.txt
RUN pip install diploma-frontend-0.6.tar.gz

CMD [ "python", "backend/manage.py", "runserver", "0.0.0.0:8000"]