############################################################
# Dockerfile to build MongoDB container images
# Based on Ubuntu
############################################################

FROM python:latest
LABEL maintainer = "Justin en Olaf"

WORKDIR /usr/app/src

COPY  test.py .

CMD ["python", "test.py"]

