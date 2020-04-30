import json
from zoomus import ZoomClient

from django.conf import settings


def get_client():
    client = ZoomClient(settings.ZOOM_API_KEY, settings.ZOOM_API_SECRET)
    return client