## syntax=docker/dockerfile:1
FROM python:3.8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY . /code/
WORKDIR /code
RUN apt-get update &&\
    apt-get install -y binutils libproj-dev gdal-bin fiona libsqlite3-mod-spatialite
RUN pip install --upgrade pip
COPY requirements.txt /code
## example
RUN mkdir /code/data/WORK/NewPhotos24  
## empty file to be filled by initial number, e.g., 0
RUN echo "" > /code/data/RENAME/last_number.txt
##RUN touch /code/data/RENAME/last_number.txt
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

