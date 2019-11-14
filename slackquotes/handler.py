# Standard library imports
import json
import os
import random

from enum import Enum

# Third party imports
import slack
from slack.errors import SlackApiError

# Local imports
from dao import hippocampus

USERNAME = 'Labby'
ICON_URL = 'https://labby-public-assets.s3.amazonaws.com/labby-small.png'

def drop_quotes(event, context):
    print('\n========================================================================')
    print("Getting all quote channels")
    channel_records = hippocampus.get_all_quote_channels()
    print("Got {} quote channels".format(len(channel_records)))
    
    print("Getting all quotes")
    quote_records = hippocampus.get_all_quotes()
    print("Got {} quotes".format(len(quote_records)))
    
    # TODO: This is the legacy method for authenticating to the API, need to get Labby registered as an app
    print("Getting slack client")
    slack_api_token = os.environ["SLACK_API_TOKEN"]
    client = slack.WebClient(token=slack_api_token)

    
    for channel_record in channel_records:

        if(not is_channel_record_valid(channel_record)):
            print("Invalid channel record\n".format(channel_record))
            continue
        
        channel_name = channel_record['fields']['Channel Name']
        
        quote_record = random.choice(quote_records)
        if(not is_quote_record_valid(quote_record)):
            print("Invalid quote record\n".format(quote_record))
            continue
        
        quote  = quote_record['fields']['Quote']
        source = quote_record['fields']['Source']
        
        formatted_quote = "\"{}\" - {}".format(quote, source)
    
        print("Posting quote to channel {}: {}".format(channel_name, formatted_quote))
        try:
            response = client.chat_postMessage(channel     = channel_name,
                                               text        = formatted_quote,
                                               username    = USERNAME,
                                               icon_url    = ICON_URL,
                                               parse       = 'full')
        except SlackApiError as error:
            print("Failed to post message: {}".format(error))
        else:
            if(response['ok'] != True):
                print('Slack response not ok: {}-{}'.format(response.status_code, response['error']))
        
    print('========================================================================\n')
        
        
def is_channel_record_valid(record) -> bool:
    if('fields' not in record):
        print("Quote record has no fields")
        return False
    
    if('Channel Name' not in record['fields']):
        print("Quote record has no 'Channel Name' field")
        return False
    
    return True

def is_quote_record_valid(record) -> bool:
    if('fields' not in record):
        print("Quote record has no fields")
        return False

    if('Quote' not in record['fields']):
        print("Quote record has no 'Quote' field")
        return False
    
    if('Source' not in record['fields']):
        print("Quote record has no 'Source' field")
        return False
    
    return True
