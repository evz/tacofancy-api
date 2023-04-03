FROM python:3-bullseye
WORKDIR /code

RUN apt-get update
RUN apt-get install -y libpq-dev build-essential

COPY requirements.txt requirements.txt
RUN pip --trusted-host files.pythonhosted.org install -r requirements.txt
COPY . .
RUN chmod a+wx /code/entrypoint.sh
CMD ["./entrypoint.sh"]
