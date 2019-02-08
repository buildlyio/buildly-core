from django.conf import settings

from celery import Celery
from celery.utils.log import get_logger
from kombu import Exchange, Queue

logger = get_logger(__name__)

# Define the URL that broker will use to connect and serializers
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

# Define default Message Routing
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#message-routing
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


# Rewrite tasks on_failure and on_success attributes
def failure_handler(self, exc, task_id, args, kwargs, einfo):
    logger.error('{0!r}'.format(exc))
    logger.error('{0!r}'.format(args))


app.conf.task_annotations = {'*': {'on_failure': failure_handler}}

# Defines the default policy when retrying publishing a task message
# in the case of connection loss or other connection errors
RETRY_POLICY = {
    'max_retries': 3,
    'interval_start': 0,
    'interval_step': 0.2,
    'interval_max': 0.2,
}

app.conf.task_publish_retry_policy = RETRY_POLICY

# Tracebacks will be included to the workers stack when re-raising task errors
app.conf.task_remote_tracebacks = True

# Tasks results will ignored
app.conf.task_ignore_result = True
