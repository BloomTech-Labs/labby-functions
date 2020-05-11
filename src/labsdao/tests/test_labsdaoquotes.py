import unittest
import unittest.mock as mock

import labsdao.quotes


@mock.patch('airtable.Airtable.__init__', mock.Mock(return_value=None))
@mock.patch('airtable.Airtable.get_all')
class TestGetAllQuotes(unittest.TestCase):

    def test_no_quotes(self, mock_airtable_get_all):

        # No quotes
        mock_airtable_get_all.return_value = []

        quotes = labsdao.quotes.get_all_quotes()

        mock_airtable_get_all.assert_called_once()

        self.assertEqual(len(quotes), 0)

    def test_bad_quote(self, mock_airtable_get_all):

        # Send something through
        quotes_in = [{"Something"}]
        mock_airtable_get_all.return_value = quotes_in

        quotes_out = labsdao.quotes.get_all_quotes()

        mock_airtable_get_all.assert_called_once()

        self.assertEqual(quotes_in, quotes_out)


@mock.patch('airtable.Airtable.__init__', mock.Mock(return_value=None))
@mock.patch('airtable.Airtable.get_all')
class TestGetAllQuoteChannels(unittest.TestCase):

    def test_no_quotes(self, mock_airtable_get_all):

        # No quotes
        mock_airtable_get_all.return_value = []

        quote_channels = labsdao.quotes.get_all_quote_channels()

        mock_airtable_get_all.assert_called_once()

        self.assertEqual(len(quote_channels), 0)

    def test_bad_quote(self, mock_airtable_get_all):

        # Send something through
        quote_channels_in = [{"Something"}]
        mock_airtable_get_all.return_value = quote_channels_in

        quote_channels_out = labsdao.quotes.get_all_quote_channels()

        mock_airtable_get_all.assert_called_once()

        self.assertEqual(quote_channels_in, quote_channels_out)
