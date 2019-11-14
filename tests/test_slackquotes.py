import pytest
import slackquotes

def test_is_channel_record_valid_no_input():
  with pytest.raises(TypeError):
    slackquotes.is_channel_record_valid()
    
def test_is_channel_record_valid_empty():
  test_record = {}
  assert slackquotes.is_channel_record_valid(record=test_record) == False
  
def test_is_channel_record_valid_no_channel_name():
  test_record = {'fields': {}}
  assert slackquotes.is_channel_record_valid(record=test_record) == False
  
def test_is_channel_record_valid_with_channel_name():
  test_record = {'fields': {'Channel Name': "Test Channel"}}
  assert slackquotes.is_channel_record_valid(record=test_record) == True