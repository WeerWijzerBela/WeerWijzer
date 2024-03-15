FROM python:3.9

ADD main.py .
ADD requirements.txt .

RUN pip install requirements.txt

CMD ["python", "main.py"]