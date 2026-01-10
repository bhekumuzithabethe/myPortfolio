#Base image
FROM python:3.13.5

#Set environmental variables
ENV PYTHONDONOTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

#Decleare a working environment
WORKDIR /app

#Copy requirements.txt
COPY  requirements.txt .

#Inatall dependancies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


COPY . .
#Expose port
EXPOSE 8000

# Run migrations and start the server
CMD ["sh", "-c", "python manage.py collectstatic --noinput && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
#Base image
FROM python:3.13.5

#Set environmental variables
ENV PYTHONDONOTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

#Decleare a working environment
WORKDIR /app

#Copy requirements.txt
COPY  requirements.txt .

#Inatall dependancies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


COPY . .
#Expose port
EXPOSE 8000

# Run migrations and start the server
CMD ["sh", "-c", "python manage.py collectstatic --noinput && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
