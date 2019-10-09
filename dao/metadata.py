# Third party imports
from airtable import Airtable

def get_all_active() -> list:
  """
  Retrieves all records repetitively and returns a single list.
  
  Returns:
      records (``list``): List of Records
  """
  airtable = Airtable('appJ2MpPg4tBiJhOC', 'Product Github Repos')

  return airtable.get_all(formula="Active = TRUE()")

def update(record_id, record_fields) -> None:
  airtable = Airtable('appJ2MpPg4tBiJhOC', 'Product Github Repos')

  response = airtable.update(record_id, record_fields)
  print(str(response))