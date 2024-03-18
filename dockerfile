FROM python:3.9

ADD main.py .
ADD requirements.txt .
WORKDIR ./

RUN pip install -r requirements.txt

CMD ["uvicorn", "WeerWijzerAPI:app --reload"]