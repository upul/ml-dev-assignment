FROM python:3.8

RUN python3 -m venv /opt/venv

COPY . /app
WORKDIR /app

# Note: We didn't create a separate virtual environment inside the docker container. 
# Doker is itself an isolated environment. 
# Hence, no need to create a virtual environment inside a docker container. 

RUN pip install -r requirements.txt

ENV PYTHONPATH /app

ENTRYPOINT ["python3", "./sentiment/app/api.py"]
