from __future__ import absolute_import

import json
import logging

from channels.sessions import channel_session

from .tasks import realTimeFaceProcess
from .models import Job

log = logging.getLogger(__name__)

@channel_session
def ws_connect(message):
    print "a client connected"
    message.reply_channel.send({
        "text": json.dumps({
            "status": "200",
            "message": "Websocket connected: " + str(message.reply_channel.name),
        })
    })

@channel_session
def ws_receive(message):
    try:
        data = json.loads(message['text'])
    except ValueError:
        log.debug("Ws message is not in json format text=%s", message['text'])
        return

    if data:
        reply_channel = message.reply_channel.name

        if data['action'] == "avatar":
            start_process(data, reply_channel)

def start_process(data, reply_channel):
    job = Job(
        img=data['img'],
        status="started",
    )
    job.save()

    #add the task to message broker
    realtime_task = realTimeFaceProcess.delay(job.id, reply_channel)

    #store the celeryid, so we are able to cancel the task when ws closed
    job.celery_id = realtime_task.id
    job.save()


