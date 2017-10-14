from fabric.api import local, run, env, put, sudo, parallel
from fabric.context_managers import cd
import os, time


env.hosts = []
env.user = 'ubuntu'
env.password = ''

def set_hosts():
    print ('getting hosts ip address from local .txt file')
    env.hosts = open('ips.txt', 'r').readlines()

def set_workers():
    env.hosts = open('workers.txt', 'r').readlines()


@parallel
def push_shape_predictors():
    put ('../../shape_predictor_68_face_landmarks.dat', '/home/ubuntu')

@parallel
def update_files():
    print env.hosts
    put('../../server', '/home/ubuntu')
    with cd('~/server'):
        sudo('pip install -r requirements.txt')

def run_master():
    with cd('~/server/realtime_channels'):
        run('python manage.py makemigrations')
        run('python manage.py migrate')
        run('python manage.py runserver')

@parallel
def run_workers():
    with cd('~/server/realtime_channels'):
        run('screen -d -m celery worker -A realtime_channels --purge -l info; sleep 5')
        time.sleep(10)

