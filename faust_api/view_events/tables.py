"""Tables for view events."""
from faust_api.app import app
from faust_api.view_events.models import MediaStats
# from datetime import timedelta


media_table = app.Table('media', value_type=MediaStats)

# Table that stores data in tumbling windows and uses the timestamp of the ViewEvent
# media_table = app.Table('media', value_type=MovieStats).tumbling(timedelta(minutes=5)) \
#     .relative_to_field(ViewEvent.DateTime)


