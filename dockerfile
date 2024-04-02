#uses the python 3.9 image
FROM python:3.9
#copies everything to the working directory
COPY . .
COPY ./templates/pictures /templates/pictures
ARG DB_HOST
ARG DB_NAME
ARG DB_PORT
ARG DB_USER
ARG DB_PASSWORD
ARG API_KEY
#copies the requirements.txt file to the working directory
ADD requirements.txt .
#sets the working directory
WORKDIR ./
#installs the requirements
RUN pip install -r requirements.txt
#exposes port 8000
EXPOSE 8000
#runs the app
CMD ["uvicorn", "WeerWijzerAPI:app", "--host", "0.0.0.0",  "--port", "8000"]