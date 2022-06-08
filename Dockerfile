# syntax=docker/dockerfile:1
FROM python:bullseye
RUN mkdir app
COPY . ./app
RUN pip install -r app/yolov5/requirements.txt
RUN pip install -r app/requirements.txt
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
WORKDIR /app
CMD python3 manage.py runserver 0.0.0.0:8000
EXPOSE 8000