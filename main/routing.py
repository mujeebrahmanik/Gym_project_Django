from django.urls import re_path
from .consumer import *

ws_patterns=[
    re_path(r'^ws/trainer_notification/$', TrainerNotificationConsumer.as_asgi()),
]
