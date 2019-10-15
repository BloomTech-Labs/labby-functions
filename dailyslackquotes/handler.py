# Standard library imports
import json
import os
import random

from enum import Enum

# Third parth imports
import slack

# Local imports
from dao import hippocampus

USERNAME = 'Labby'
ICON_URL = 'https://labby-public-assets.s3.amazonaws.com/labby-small.png'

def drop_quotes(event, context):
    print("Getting all hiring manager quote channels")
    quote_channels = hippocampus.get_all_hiring_manager_quote_channels()
    print("Got {} quote channels".format(len(quote_channels)))
    
    print("Getting all hiring manager quotes")
    quote_records = hippocampus.get_all_hiring_manager_quotes()
    print("Got {} quotes".format(len(quote_records)))
    
    # TODO: This is the legacy method for authenticating to the API
    print("Getting slack client")
    slack_api_token = os.environ["SLACK_API_TOKEN"]
    client = slack.WebClient(token=slack_api_token)

    for channel in quote_channels:
        channel_name = channel['fields']['Channel Name']
        
        random_record = random.choice(quote_records)
        raw_quote = random_record['fields']['Quote']
        formatted_quote = "\"{}\" - A Real Hiring Manager".format(raw_quote)
    
        print("Posting quote to channel {}: {}".format(channel_name, formatted_quote))
        response = client.chat_postMessage(
            channel     = channel_name,
            text        = formatted_quote,
            username    = USERNAME,
            icon_url    = ICON_URL)

        print("Response: {}".format(response))
        if(response['ok'] != True):
            raise Exception('Slack response not ok: {}-{}'.format(response.status_code, response['error']))