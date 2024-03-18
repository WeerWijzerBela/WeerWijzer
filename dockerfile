FROM python:3.9

ADD . .
ADD requirements.txt .
WORKDIR ./

RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "WeerWijzerAPI:app", "--host", "0.0.0.0",  "--port", "8000"]

