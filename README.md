# 2DAnimoji

*A realtime web based 2D Animoji implemented with WebSockets and Distributed Backend.*

![Alt Text](https://s3-us-west-1.amazonaws.com/yulongchenblog/demo.gif)

# Workflow
![Alt Text](https://s3-us-west-1.amazonaws.com/yulongchenblog/2DAnimojiWorkFlow.png)

### Back-end
Python Django Channels (Handle WebSockets) <br />
Python Celery (Distributed task queue) <br />
Python Flower (Realtime Celery monitoring tool) <br />
Python Fabric (Application deployment tool) <br /> 
Redis (Message broker) <br />
PostgreSQL (Shared database) <br />
OpenCV (Computer vision library) <br />
dlib (Machine learning library for facial data extraction) <br />

### Front-end
WebcamJS (Webcam image capture library) <br />
WebGL + Live2D SDK (2D Model) <br />
WebSockets

# Usage

###Database setup
In /etc/enviroment, add 
DJANGO_DB_ENGINE="django.db.backends.postgresql" <br />
DJANGO_DB_NAME="Your database name" <br />
DJANGO_DB_USER="Your database user name" <br />
DJANGO_DB_PASSWORD="Your database password" <br />
DJANGO_DB_HOST="Your database host" <br />
DJANGO_DB_PORT="Your database port" <br />
REDIS_ADDRESS="Your redis IP address" <br />


I hosted my PostgreSQL database on AWS RDS, and here is my setup example <br />
DJANGO_DB_ENGINE="django.db.backends.postgresql" <br />
DJANGO_DB_NAME="demo" <br />
DJANGO_DB_USER="xxx" <br />
DJANGO_DB_PASSWORD="xxxx" <br />
DJANGO_DB_HOST="demo.csdffhk1sdfsd.us-west-1.rds.amazonaws.com" <br />
DJANGO_DB_PORT="5432" <br />
REDIS_ADDRESS="114.21.23.3:6379" <br />

###Master setup
Under /server/realtime_channels <br />

```
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
###Worker setup

Under /server/realtime_channels <br />

```
celery worker -A realtime_channels --purge -l info
```

###Deployment script


Under /server/deploy <br />
Push the code to servers: <br />

```
fab set_hosts update_files
```
Run all the workers: <br />

```
fab set_workers run_workers
```

###Realtime worker monitoring
 
```
celery flower -A realtime_channels --address=0.0.0.0 --port=5555
```

Screenshot:
 ![](https://s3-us-west-1.amazonaws.com/yulongchenblog/celeryflower.png)