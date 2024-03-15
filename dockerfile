FROM python:3.9

ADD main.py .
ADD requirements.txt .
WORKDIR ./

RUN pip install requirements.txt --user

CMD ["python", "main.py"]