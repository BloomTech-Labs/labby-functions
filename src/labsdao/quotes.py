# Core imports
import os

# Third party imports
from airtable import Airtable

HIPPOCAMPUS_BASE_ID = "appThDY89pV0kOGQT"

QUOTES_TABLE_NAME = "Labby Quotes"

QUOTE_CHANNELS_TABLE_NAME = "Labby Quote Channels"


def get_all_quotes() -> list:
    """
    Returns a list of all the quotes

    Returns:
        records (``list``): List of quotes
    """
    airtable = Airtable(HIPPOCAMPUS_BASE_ID, QUOTES_TABLE_NAME, api_key=os.environ["AIRTABLE_API_KEY"])

    return airtable.get_all(formula="Active = TRUE()")


def get_all_quote_channels() -> list:
    """
    Returns a list of all the channels to drop quotes into

    Returns:
        records (``list``): List of channels
    """
    airtable = Airtable(HIPPOCAMPUS_BASE_ID, QUOTE_CHANNELS_TABLE_NAME, api_key=os.environ["AIRTABLE_API_KEY"])

    return airtable.get_all(formula="Active = TRUE()")
