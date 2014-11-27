#!/usr/bin/env python

import unittest
import random
from __init__ import CueCloud

TEST_API_KEY='42cef2c79a984e34'
TEST_API_PASS='2152b0f3cc1649fb'
TEST_CC_LAST_FOUR = '1111'
PAY_AMOUNT = float('%.2f' % (10.24 + random.random()))
NUM_OPPS = 4
CUECLOUD_FEE = 0.10 # 10%


class TestCueCloud(unittest.TestCase):

    def setUp(self):
        self.cuecloud = CueCloud(TEST_API_KEY, TEST_API_PASS)
        self.cue_id = None
        self.cue_completion_id = None

    def test001_validate_user(self):
        res = self.cuecloud.validate_user()
        self.assertEquals(res['StatusCode'], 0)
    
    def test002_get_keywords(self):
        res = self.cuecloud.get_keywords()
        self.assertIn('facebook', res['Data']['Keywords'])
    
    def test003_make_deposit(self):
        previous_balance = self.cuecloud.get_balance()['Data']['Balance']
        self.cuecloud.make_deposit(amount_in_usd=PAY_AMOUNT, cc_last_four=TEST_CC_LAST_FOUR)
        new_balance = self.cuecloud.get_balance()['Data']['Balance']
        self.assertAlmostEqual(PAY_AMOUNT, abs(new_balance - previous_balance))
    	
    def test004_withdraw_funds(self):
        previous_balance = self.cuecloud.get_balance()['Data']['Balance']
        self.cuecloud.withdraw_funds(amount_in_usd=PAY_AMOUNT)
        new_balance = self.cuecloud.get_balance()['Data']['Balance']        
        self.assertAlmostEqual(PAY_AMOUNT, abs(new_balance - previous_balance))

    def test005_create_cue(self):
        previous_num_cues = self.cuecloud.get_cues()['Data']['NumTotalResults']
        previous_balance = self.cuecloud.get_balance()['Data']['Balance']
        new_cue = self.cuecloud.create_cue(title="New Cue", amount=PAY_AMOUNT, num_opportunities=NUM_OPPS)
        new_num_cues = self.cuecloud.get_cues()['Data']['NumTotalResults']
        new_balance = self.cuecloud.get_balance()['Data']['Balance']
        self.assertGreater(new_num_cues, previous_num_cues)
        balance_difference = abs(previous_balance - new_balance)
        difference_should_be = float('%.2f' % (float(PAY_AMOUNT) * NUM_OPPS * (1 + CUECLOUD_FEE)))
        self.assertAlmostEqual(balance_difference, difference_should_be)

    def test006_submit_cue_completion(self):
        last_cue_id = self.cuecloud.get_cues()['Data']['Cues'][0]['ID']
        previous_num_completions = self.cuecloud.get_cue_completions(last_cue_id)['Data']['NumTotalResults']
        assignment_id = self.cuecloud.assign_cue(last_cue_id)['Data']['AssignmentID']
        completion_id = self.cuecloud.submit_cue_completion(
                         assignment_id=assignment_id, answer_text='My Answer')['Data']['CueCompletionID']
        new_num_completions = self.cuecloud.get_cue_completions(last_cue_id)['Data']['NumTotalResults']
        self.assertGreater(new_num_completions, previous_num_completions)

    def test007_grant_bonus(self):
        previous_num_payments = self.cuecloud.get_payments()['Data']['NumTotalResults']
        last_cue_id = self.cuecloud.get_cues(has_pending_cue_completions=True)['Data']['Cues'][0]['ID']
        last_cue_completion_id = self.cuecloud.get_cue_completions(last_cue_id)['Data']['CueCompletions'][0]['ID']
        self.cuecloud.grant_bonus(cue_completion_id=last_cue_completion_id, amount=PAY_AMOUNT, reason='Nice work')
        new_num_payments = self.cuecloud.get_payments()['Data']['NumTotalResults']
        self.assertGreater(new_num_payments, previous_num_payments)

    def test008_decline_cue_completion(self):
        last_cue_id = self.cuecloud.get_cues()['Data']['Cues'][0]['ID']
        previous_num_pending_cue_completions = self.cuecloud.get_cues(last_cue_id)['Data']['Cues'][0]['NumberOfCueCompletionsPendingReview']
        pending_cue_completion_id_to_approve = self.cuecloud.get_cue_completions(last_cue_id, status='Pending')['Data']['CueCompletions'][0]['ID']
        self.cuecloud.decline_cue_completion(cue_completion_id=pending_cue_completion_id_to_approve)
        new_num_pending_cue_completions = self.cuecloud.get_cues(last_cue_id)['Data']['Cues'][0]['NumberOfCueCompletionsPendingReview']
        self.assertLess(new_num_pending_cue_completions, previous_num_pending_cue_completions)
    
    def test009_accept_cue_completion(self):
        last_cue_id = self.cuecloud.get_cues()['Data']['Cues'][0]['ID']
        previous_num_approved_cue_completions = self.cuecloud.get_cues(last_cue_id)['Data']['Cues'][0]['NumberOfCueCompletionsApproved']
        cue_completion_id_to_approve = self.cuecloud.get_cue_completions(last_cue_id, status='Canceled')['Data']['CueCompletions'][0]['ID']
        self.cuecloud.approve_cue_completion(cue_completion_id=cue_completion_id_to_approve)
        new_num_approved_cue_completions = self.cuecloud.get_cues(last_cue_id)['Data']['Cues'][0]['NumberOfCueCompletionsApproved']
        self.assertGreater(new_num_approved_cue_completions, previous_num_approved_cue_completions)
    
    def test010_cancel_cue(self):
        previous_num_active_cues = self.cuecloud.get_cues(status='Active')['Data']['NumTotalResults']
        cue_id = self.cuecloud.get_cues(status='Active')['Data']['Cues'][0]['ID']
        self.cuecloud.cancel_cue(cue_id)
        new_num_active_cues = self.cuecloud.get_cues(status='Active')['Data']['NumTotalResults']
        self.assertEqual(new_num_active_cues + 1, previous_num_active_cues)


if __name__ == "__main__":
    unittest.main()




