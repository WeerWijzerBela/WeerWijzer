############################################################
# Dockerfile to build MongoDB container images
# Based on Ubuntu
############################################################

FROM python:latest
LABEL maintainer = "Justin en Olaf"

WORKDIR ./

COPY  test.py ./

CMD ["python", "test.py"]




