FROM python:3.9

ADD . .
ADD requirements.txt .
WORKDIR ./

RUN pip install -r requirements.txt
EXPOSE 8080
CMD ["uvicorn", "WeerWijzerAPI:app"]