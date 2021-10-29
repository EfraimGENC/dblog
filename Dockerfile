FROM python:3.8
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY . /code/
RUN groupadd -r django && useradd -r -g django django
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip3 install -r requirements.txt
