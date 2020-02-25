"""Endpoints for view events."""
import json

from pandas import DataFrame
import pandas as pd

from faust_api.app import app
from faust_api.view_events.tables import media_table
from faust_api.view_events.models import ViewEvent
from faust_api.view_events.kafka_topics import events_topic
from faust import web


events = web.Blueprint('events')


@events.route('/create/', name='create')
class CreateEventView(web.View):
    async def post(self, request: web.Request) -> web.Response:
        """Create view event and publish to kafka topic.

        Args:
            request: web request with json object containing the event.

        Returns:
            If success publish to kafka topic.
            json: Status. Success for success, error for fail.
        """
        payload = await request.json()

        event_id = payload.get('EventId', None)
        if event_id is None:
            return self.json({'status': 'error',
                              'error': "Missing EventId"})

        view_event = ViewEvent.loads(json.dumps(payload))  # create ViewEvent from json
        validation_errors = view_event.validate()
        if validation_errors:
            return self.json({'status': 'error',
                              'error': [x.reason for x in validation_errors]})

        await events_topic.send(key=event_id, value=view_event)
        return self.json({'status': 'success'})


media = web.Blueprint('media')


@media.route('/getstats/{media_id}/')
class GetMediaView(web.View):
    async def get(self, request: web.Request, media_id) -> web.Response:
        """Get media statistics.

        Args:
            request:
            media_id: MediaId of the requested item.

        Returns:
            json: media statistics. Error if fail.
        """
        if int(media_id) not in media_table.keys():
            return self.json({'status': 'error',
                              'error': 'Key does not exist'})

        movie_stats = media_table[int(media_id)].dumps()  # get json representation

        return self.json({'status': 'success',
                          'data': movie_stats})


@media.route('/getsimilar/{media_id}/')
class GetSimmilarView(web.View):
    async def get(self, request: web.Request, media_id) -> web.Response:
        """Get similar media items.

        Args:
            request:
            media_id: MediaId of the requested item.

        Returns:
            json: similar item ids and their correlation. Error if fail.
        """
        if int(media_id) not in media_table.keys():
            return self.json({'status': 'error',
                              'error': 'Key does not exist'})

        # hacky version to get item, user matrix
        media_user_matrix = {}
        for key in media_table.keys():
            media_user_matrix[key] = media_table[key].user_views

        media_matrix = DataFrame(media_user_matrix).fillna(0)

        user_view_time = media_matrix[int(media_id)]

        similar_to = media_matrix.corrwith(user_view_time)  # calculate correlation

        # remove empty items and get the top 10 best scores
        correlation = pd.DataFrame(similar_to, columns=['Correlation'])
        correlation.dropna(inplace=True)
        simmilar_list = correlation.sort_values(by='Correlation', ascending=False).head(10).to_dict()

        del simmilar_list['Correlation'][int(media_id)]  # remove the item of the requested id

        return self.json({'status': 'success',
                          'data': simmilar_list})


app.web.blueprints.add('/event/', events)
app.web.blueprints.add('/media/', media)
