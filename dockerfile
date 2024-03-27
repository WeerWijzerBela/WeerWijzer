#uses the python 3.9 image
FROM python:3.9
#copies everything to the working directory
WORKDIR /app
COPY . /app/

#instlls the requirements
RUN pip install -r requirements.txt
#exposes port 8000
EXPOSE 8000
#runs the app
CMD ["uvicorn", "/app/WeerWijzerAPI:app", "--host", "0.0.0.0",  "--port", "8000"]

