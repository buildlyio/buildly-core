from __future__ import absolute_import
from celery import Celery
from kombu import Exchange, Queue

from django.conf import settings


broker_url = 'amqp://{}:{}@{}:{}/{}'.format(
    settings.RABBIT_USER, settings.RABBIT_PASS, settings.RABBIT_HOST,
    settings.RABBIT_PORT, settings.RABBIT_VHOST
)

app = Celery(
    'celery_bifrost',
    broker=broker_url,
    backend='rpc://',
    include=['web.tasks'],
    task_serializer='json',
    result_serializer='json',
    accept_content=['application/json'],
)

default_queue_name = settings.RABBIT_WALHALL_QUEUE
default_exchange_name = 'direct_web'
default_routing_key = 'service.web'
default_exchange = Exchange(default_exchange_name, type='direct')
default_queue = Queue(
    default_queue_name,
    default_exchange,
    routing_key=default_routing_key
)

app.conf.task_queues = (default_queue, )

app.conf.task_default_queue = default_queue_name
app.conf.task_default_exchange = default_exchange_name
app.conf.task_default_routing_key = default_routing_key
