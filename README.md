# NPO Assignment

To implement an endpoint that can efficiently consume a stream of view-events, which is
potentially greater than memory. 

## Getting Started

Clone the repo via ```git clone https://github.com/Janwillemtv/NPO_assignment.git```.
Go into folder ```cd NPO_assignment```

This application is based on the [Faust](https://faust.readthedocs.io/en/latest/index.html) python library. 
To run this application a kafka broker is needed.
A broker can be started using docker and docker-compose.

Included is this project is kafka-docker-master by [wurstmeister](https://github.com/wurstmeister/kafka-docker).
This kafka instance can be run using ```docker-compose -f kafka-docker-master/docker-compose-single-broker.yml up -d```
I have only changed the single-broker docker-compose file to work with this project.

After Kafka has been built and is running you can start the Faust app.
To be able to run the app you need a python 3.7 environment with pip and install the requirements,
```pip install -r requirements.txt```

Then the application can be started using ```python3 -m faust_api worker -l info```. This starts a single faust worker.

To send the provided example data to this application, you can use the data_producer script in the data_producer folder.
You need to place the test data in this data_producer folder and then run it using ```python3 producer.py```.


## Processing stream events
I chose to use the faust library because it is fast and flexible for event processing. And easy to use since its pure python, so we dont need anything extra.
(disclaimer: it is the first time i am using it, so ill probably learn if these statements are true.) 

An endpoint is created where stream events can be sent to. The events are validated against a data model and descriptive
errors are sent back to the client if some fields do not comply with the data model. The event processing is efficient 
and scalable by using the faust library, extra workers can be started if necessary.

endpoint: ```http://localhost:6066/event/create/```. The json part of the post request should contain the json serialised event.

## Provide insights
I used faust tables to store data for insights, this is where I ran in some trouble. The normal tables work just fine, they
are dictionary like tables. But I tried implementing a tumbling table, this puts the processed events into time windows, so you
can keep track of the changes over time. The processing of the events into an tumbling table worked just fine, but getting them
out to view the data was (for me) not possible in the timeframe of this assignment. These tumbling tables only seem to work well in a stream context,
so when handling an incoming event. But when accessed outside of a stream, for example an endpoint to get all the data for a
certain media item, only a single time window could be retrieved. I lost some time trying to implement these windowed tables,
it took to long, so I replaced them by time independent tables that just store the aggregated values of some media statistics.

Per media item the total viewtime, number of starts, number of stops and number of ends are stored. This information can be 
accessed through an endpoint: ```http://localhost:6066/media/getstats/{media_id}/```.

It would be nice to see trends over time, but the quirkyness of these faust tables provided some unforeseen challenges.

These tables are fast and scalable through the faust library.

## Item-item collaborative filtering
Since I lost some time on the tables the collaborative filtering is very quickly implemented.
A user viewtime field is added to each media item in the table to be able to do cf on the basis of viewtime.
When similar items are requested through an endpoint a media-user matrix is built and the correlation of each media item is calculated.
The top 10 is returned.

endpoint:```http://localhost:6066/media/getsimilar/{media_id}/```

This solution is not very fast and scalable, since all the processing is done upon request. When more users and media items are added
to the database causes the processing time to increase. A better solution would be that a media-user matrix is
updated when events come in so that its already available upon request. And i can imagine that there are smarter solutions that take
scalability into account.


