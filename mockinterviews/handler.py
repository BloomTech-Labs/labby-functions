# Standard library imports
import json
import os
import random
import datetime

from enum import Enum

# Third parth imports
import slack
from slack.errors import SlackApiError

# Local imports
from labsdao import people

USERNAME = 'Labby'
ICON_URL = 'https://labby-public-assets.s3.amazonaws.com/labby-small.png'

NOTIFICATION_DELAY_MINUTES = 5

def notify_interviewees(event, context):
    person_records = people.get_all_unscheduled_and_incomplete_interviewees()
    
    for person_record in person_records:
        if 'SMT Record ID' not in person_record['fields']:
            print("Person record {} missing SMT Record ID".format(person_record['id']))
            continue
        
        person_smt_record_id = person_record['fields']['SMT Record ID'][0]
        print("Processing person record: {}".format(person_smt_record_id))
        
        if 'Interview Scheduled' in person_record['fields']:
            print("Skipping {} because interview is scheduled".format(person_smt_record_id))
            continue
        
        person_memory_item = people.get_person_memory(person_smt_record_id)
        if 'Item' in person_memory_item and 'last_interview_notification' in person_memory_item['Item']:
            time_last_notified_string = person_memory_item['Item']['last_interview_notification']
            time_last_notified = datetime.datetime.fromisoformat(time_last_notified_string)
            
            print("Person last notified: {}".format(time_last_notified))
 
            minutes_since_notified = (datetime.datetime.utcnow() - time_last_notified).total_seconds()//60
            print("Minutes since last notification: {}".format(minutes_since_notified))
            
            if minutes_since_notified > NOTIFICATION_DELAY_MINUTES:
                print("Notifying person again")
                notify_interviewee(person_smt_record_id)
            else: 
                continue

        else:
            print("Notifying person for first time: {}".format(person_smt_record_id))
            
            # notify_interviewee(person_smt_record_id)
            
            people.notified_of_interview(person_smt_record_id)

def notify_interviewee(person_smt_record_id: str):
    person_smt_record = people.get_smt_record(person_smt_record_id)
    
    if 'Slack User ID' not in person_smt_record['fields']:
        print("User {} has no slack id".format(person_smt_record_id))
    
    slack_user_id = person_smt_record['fields']['Slack User ID'][0]
    print("Notifying interviewee: {}".format(slack_user_id))
    
    
    #     channel_name = channel_record['fields']['Channel Name']
        
    #     quote_record = random.choice(quote_records)
    #     if(not is_quote_record_valid(quote_record)):
    #         print("Invalid quote record\n".format(quote_record))
    #         continue
        
    #     quote  = quote_record['fields']['Quote']
    #     source = quote_record['fields']['Source']
        
    #     formatted_quote = "\"{}\" - {}".format(quote, source)
    
    #     print("Posting quote to channel {}: {}".format(channel_name, formatted_quote))
    #     try:
    #         response = client.chat_postMessage(channel     = channel_name,
    #                                            text        = formatted_quote,
    #                                            username    = USERNAME,
    #                                            icon_url    = ICON_URL,
    #                                            parse       = 'full')
    #     except SlackApiError as error:
    #         print("Failed to post message: {}".format(error))
    #     else:
    #         if(response['ok'] != True):
    #             print('Slack response not ok: {}-{}'.format(response.status_code, response['error']))
        
    # print('========================================================================\n')
        
def is_person_record_valid(person_record) -> bool:
    # if('fields' not in record):
    #     print("Quote record has no fields")
    #     return False
    
    # if('Channel Name' not in record['fields']):
    #     print("Quote record has no 'Channel Name' field")
    #     return False
    
    return True
