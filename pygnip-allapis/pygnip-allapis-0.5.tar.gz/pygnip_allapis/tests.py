from datetime import datetime, timedelta
import unittest
import gnip_client


class BasicTests(unittest.TestCase):

    def setUp(self):
        self.client = gnip_client.AllAPIs(config='DEFAULT')
        now = datetime.now()
        self.to_date = now.strftime("%Y%m%d0000")
        self.from_date = (now - timedelta(days=30)).strftime("%Y%m%d0000")

    def tearDown(self):
        self.client = None

    def test_usage_returns_200(self):
        response = (self.client.api(
                    'UsageAPI').get_usage(
                    decode_json=False,
                    bucket='month',
                    fromDate=self.from_date,
                    toDate=self.to_date))
        self.assertEqual(200, response.status_code)

    def test_search_returns_200(self):
        response = (self.client.api(
                    'SearchAPI').max_results_only(
                    decode_json=False,
                    query='gnip',
                    publisher='twitter',
                    fromDate=self.from_date,    
                    toDate=self.to_date,
                    maxResults='10'))
        self.assertEqual(200, response.status_code)

    def test_search_count_returns_200(self):
        response = (self.client.api(
                    'SearchAPICount').search_count(
                    decode_json=False,
                    query='gnip',
                    publisher='twitter',
                    fromDate=self.from_date,
                    toDate=self.to_date,
                    bucket='day'))
        self.assertEqual(200, response.status_code)

    def test_powertrack_can_set_rule(self):
        response = (self.client.api(
                    'PowertrackAPIRules').post_rule(value='test_rule', tag='test_rules'))
        self.assertEqual(201, response.status_code)

    def test_previously_set_rule_exists(self):
        response = (self.client.api(
                    'PowertrackAPIRules').get_rules(decode_json=False))
        #TO DO: assert value:rule2 in response.json()
        self.assertEqual(200, response.status_code)

    def test_powertrack_can_delete_previously_set_rule(self):
        response = (self.client.api(
                    'PowertrackAPIRules').delete_rule(value='test_rule', tag='test_rules'))
        self.assertEqual(200, response.status_code)

    def test_rule_no_longer_exists(self):
        response = (self.client.api(
                    'PowertrackAPIRules').get_rules(decode_json=False))
        #TO DO: assert value:rule2 not in response.json()
        self.assertEqual(200, response.status_code)    

if __name__ == '__main__':
    unittest.main()
