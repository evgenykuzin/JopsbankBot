FROM python:3.8-slim-buster

WORKDIR /app

#ENV PYTHONPATH = /workspace

COPY requirements.txt requirements.txt

RUN  python3.6 -m pip install --upgrade pip
RUN  python3.6 -m pip install -r requirements.txt

COPY . .

RUN python3.6 -m setup.py

CMD [ "python", "main.py" ]