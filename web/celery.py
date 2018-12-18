from __future__ import absolute_import
from django.conf import settings

from celery import Celery
from kombu import Exchange, Queue

broker_url = 'amqp://{}:{}@{}:{}/{}'.format(
    settings.RABBIT_USER, settings.RABBIT_PASS, settings.RABBIT_HOST,
    settings.RABBIT_PORT, settings.RABBIT_VHOST
)

app = Celery(
    'celery_bifrost',
    broker=broker_url,
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

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
