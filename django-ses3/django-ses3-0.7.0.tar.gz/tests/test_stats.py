# coding: utf-8
from __future__ import unicode_literals

from django.test import TestCase

from django_ses.views import (emails_parse, stats_to_list, quota_parse,
    sum_stats)

# Mock of what boto's SESConnection.get_send_statistics() returns
STATS_DICT = {
    'GetSendStatisticsResponse': {
        'GetSendStatisticsResult': {
            'SendDataPoints': [
                {
                    'Bounces': '1',
                    'Complaints': '0',
                    'DeliveryAttempts': '11',
                    'Rejects': '0',
                    'Timestamp': '2011-02-28T13:50:00Z',
                },
                {
                    'Bounces': '1',
                    'Complaints': '0',
                    'DeliveryAttempts': '3',
                    'Rejects': '0',
                    'Timestamp': '2011-02-24T23:35:00Z',
                },
                {
                    'Bounces': '0',
                    'Complaints': '2',
                    'DeliveryAttempts': '8',
                    'Rejects': '0',
                    'Timestamp': '2011-02-24T16:35:00Z',
                },
                {
                    'Bounces': '0',
                    'Complaints': '2',
                    'DeliveryAttempts': '33',
                    'Rejects': '0',
                    'Timestamp': '2011-02-25T20:35:00Z',
                },
                {
                    'Bounces': '0',
                    'Complaints': '0',
                    'DeliveryAttempts': '3',
                    'Rejects': '3',
                    'Timestamp': '2011-02-28T23:35:00Z',
                },
                {
                    'Bounces': '0',
                    'Complaints': '0',
                    'DeliveryAttempts': '2',
                    'Rejects': '3',
                    'Timestamp': '2011-02-25T22:50:00Z',
                },
                {
                    'Bounces': '0',
                    'Complaints': '0',
                    'DeliveryAttempts': '6',
                    'Rejects': '0',
                    'Timestamp': '2011-03-01T13:20:00Z',
                },
            ],
        }
    }
}

QUOTA_DICT = {
    'GetSendQuotaResponse': {
        'GetSendQuotaResult': {
            'Max24HourSend': '10000.0',
            'MaxSendRate': '5.0',
            'SentLast24Hours': '1677.0'
        },
        'ResponseMetadata': {
            'RequestId': '8f100233-44e7-11e0-a926-a198963635d8'
        }
    }
}

VERIFIED_EMAIL_DICT = {
    'ListVerifiedEmailAddressesResponse': {
        'ListVerifiedEmailAddressesResult': {
            'VerifiedEmailAddresses': [
                'test2@example.com',
                'test1@example.com',
                'test3@example.com'
            ]
        },
        'ResponseMetadata': {
            'RequestId': '9afe9c18-44ed-11e0-802a-25a1a14c5a6e'
        }
    }
}


class StatParsingTest(TestCase):
    def setUp(self):
        self.stats_dict = STATS_DICT
        self.quota_dict = QUOTA_DICT
        self.emails_dict = VERIFIED_EMAIL_DICT

    def test_stat_to_list(self):
        expected_list = [
            {
                'Bounces': '0',
                'Complaints': '2',
                'DeliveryAttempts': '8',
                'Rejects': '0',
                'Timestamp': '2011-02-24T16:35:00Z',
            },
            {
                'Bounces': '1',
                'Complaints': '0',
                'DeliveryAttempts': '3',
                'Rejects': '0',
                'Timestamp': '2011-02-24T23:35:00Z',
            },
            {
                'Bounces': '0',
                'Complaints': '2',
                'DeliveryAttempts': '33',
                'Rejects': '0',
                'Timestamp': '2011-02-25T20:35:00Z',
            },
            {
                'Bounces': '0',
                'Complaints': '0',
                'DeliveryAttempts': '2',
                'Rejects': '3',
                'Timestamp': '2011-02-25T22:50:00Z',
            },
            {
                'Bounces': '1',
                'Complaints': '0',
                'DeliveryAttempts': '11',
                'Rejects': '0',
                'Timestamp': '2011-02-28T13:50:00Z',
            },
            {
                'Bounces': '0',
                'Complaints': '0',
                'DeliveryAttempts': '3',
                'Rejects': '3',
                'Timestamp': '2011-02-28T23:35:00Z',
            },
            {
                'Bounces': '0',
                'Complaints': '0',
                'DeliveryAttempts': '6',
                'Rejects': '0',
                'Timestamp': '2011-03-01T13:20:00Z',
            },
        ]
        actual = stats_to_list(self.stats_dict, localize=False)

        self.assertEqual(len(actual), len(expected_list))
        self.assertEqual(actual, expected_list)

    def test_quota_parse(self):
        expected = {
            'Max24HourSend': '10000.0',
            'MaxSendRate': '5.0',
            'SentLast24Hours': '1677.0',
        }
        actual = quota_parse(self.quota_dict)

        self.assertEqual(actual, expected)

    def test_emails_parse(self):
        expected_list = [
            'test1@example.com',
            'test2@example.com',
            'test3@example.com',
        ]
        actual = emails_parse(self.emails_dict)

        self.assertEqual(len(actual), len(expected_list))
        self.assertEqual(actual, expected_list)

    def test_sum_stats(self):
        expected = {
            'Bounces': 2,
            'Complaints': 4,
            'DeliveryAttempts': 66,
            'Rejects': 6,
        }

        stats = stats_to_list(self.stats_dict)
        actual = sum_stats(stats)

        self.assertEqual(actual, expected)
