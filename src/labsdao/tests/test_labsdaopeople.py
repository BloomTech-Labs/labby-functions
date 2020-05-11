import unittest
import unittest.mock as mock

import labsdao.people


@mock.patch('airtable.Airtable.__init__', mock.Mock(return_value=None))
@mock.patch('airtable.Airtable.get')
class TestGetSMTRecord(unittest.TestCase):

    def test_no_record(self, mock_airtable_get):

        # No SMT record ID
        mock_airtable_get.return_value = None

        labsdao.people.get_smt_record.cache_clear()

        smt_record = labsdao.people.get_smt_record("12345")

        mock_airtable_get.assert_called_once()

        self.assertEqual(smt_record, None)

    def test_happy(self, mock_airtable_get):

        # Send something through
        record_in = "Something"
        mock_airtable_get.return_value = record_in

        record_out = labsdao.people.get_smt_record("12345")

        mock_airtable_get.assert_called_once()

        self.assertEqual(record_in, record_out)


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
