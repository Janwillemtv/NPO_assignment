"""Agents for handling view events"""
from faust_api.app import app
from faust_api.view_events.kafka_topics import events_topic
from faust_api.view_events.models import MediaStats, ViewEvent
from faust_api.view_events.tables import media_table
import logging


@app.agent(events_topic)
async def process_event(events):
    """Agent for processing events and storing them in a table.

    Args:
        events: ViewEvent object

    Returns:

    """
    async for event in events:
        # process infinite stream of events.

        # needed for tumbling table
        # try:
        #     media_stats = media_table[event.MediaId].value()
        # except KeyError:
        #     media_stats = MovieStats()

        if event.MediaId in media_table:
            media_stats = media_table[event.MediaId]
        else:
            media_stats = MediaStats()

        if event.UserId in media_stats.user_views:
            user_viewtime = media_stats.user_views[event.UserId]
        else:
            user_viewtime = 0

        if event.EventType == ViewEvent.WAYPOINT:
            media_stats.view_time += 30
            user_viewtime += 30

        elif event.EventType == ViewEvent.STREAMSTART:
            media_stats.starts += 1

        elif event.EventType == ViewEvent.STREAMSTOP:
            media_stats.stops += 1

        elif event.EventType == ViewEvent.STREAMEND:
            media_stats.ends += 1

        else:
            logging.warning('EventType does not exist')

        media_stats.user_views[event.UserId] = user_viewtime
        media_table[event.MediaId] = media_stats
