"""Kafka topics for handling events"""

from faust_api.app import app
from faust_api.view_events.models import ViewEvent

events_topic = app.topic('events', value_type=ViewEvent)
