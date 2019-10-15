"""Various things in Labby's memory"""

# Third party imports
from airtable import Airtable

HIPPOCAMPUS_BASE_ID = 'appThDY89pV0kOGQT'

HIRING_MANAGER_QUOTES_TABLE_NAME = 'Labby Hiring Manager Quotes'
HIRING_MANAGER_QUOTE_CHANNELS_TABLE_NAME = 'Labby Hiring Manager Quote Channels'

def get_all_hiring_manager_quotes() -> list:
  """
  Returns a list of all the hiring manager quotes
  
  Returns:
      records (``list``): List of quotes
  """
  airtable = Airtable(HIPPOCAMPUS_BASE_ID, HIRING_MANAGER_QUOTES_TABLE_NAME)

  return airtable.get_all(formula="Active = TRUE()")

def get_all_hiring_manager_quote_channels() -> list:
  """
  Returns a list of all the channles to drop hiring manager quotes
  
  Returns:
      records (``list``): List of channels
  """
  airtable = Airtable(HIPPOCAMPUS_BASE_ID, HIRING_MANAGER_QUOTE_CHANNELS_TABLE_NAME)

  return airtable.get_all(formula="Active = TRUE()")
