import os
import requests
from datetime import datetime
import time
import hmac
import hashlib
import socket
import urllib
try:
    import json
except ImportError:
    import simplejson as json

API_VERSION = 'api/v1.0/'
LOCAL_DEVELOPERS = ['Davids-iMac.local', 'kilo.local']
if socket.gethostname() in LOCAL_DEVELOPERS:
    DEFAULT_BASE_URL = 'http://localhost:8000/'
else:
    DEFAULT_BASE_URL = 'https://cuecloud.com/'


class CueCloudError(Exception):
    pass


class CueCloud(object):

    def __init__(self, api_key=None, api_pass=None, base_url=None):
	
        if not base_url:
            base_url = os.path.join(DEFAULT_BASE_URL, API_VERSION)

        if not api_key:
            try:
                api_key = os.environ['CUECLOUD_ACCESS_KEY']
            except KeyError:
                raise CueCloudError('CUECLOUD_ACCESS_KEY not set.')

        if not api_pass:
            try:
                api_pass = os.environ['CUECLOUD_ACCESS_PASSWORD']
            except KeyError:
                raise CueCloudError('CUECLOUD_ACCESS_PASSWORD not set.')

        self.base_url = base_url
        self.api_key = api_key
        self.api_pass = api_pass


    def _build_request(self, url, data=None):
        """
        The signature is a concatenation of nonce + url + body.
        A GET request will have no body, a POST request will.
        """
        if not url:
            raise CueCloudError('A url must be specified.')
        
        nonce = str(int(time.time() * 1e6))
        if data:
            body = json.dumps(data)
        else:
            body = ''
        
        message = nonce + url + body
        signature = hmac.new(self.api_pass, message, hashlib.sha256).hexdigest()
        headers = {
            'Access-Key': self.api_key,
            'Access-Signature': signature,
            'Access-Nonce': nonce,
            'Content-Type': 'application/json',
        }
        # print headers
        
        if data:
            r = requests.post(url, headers=headers, data=body)
        else:
            r = requests.get(url, headers=headers)

        try:
            r_data = r.json()
        except: # most likely a JSONDecodeError
            raise CueCloudError(r)

        print '***', r_data['Error']
        return r_data


    def validate_user(self):
        '''
        This is a test method to make sure that
        the user has valid API credentials.
        '''
        method_path = 'validate/'
        url = os.path.join(self.base_url, method_path)
        return self._build_request(url)


    def get_keywords(self):
        '''
        This will return common keywords for Cues.
        Useful for CueCreation.
        '''
        method_path = 'cues/keywords/'
        url = os.path.join(self.base_url, method_path)
        return self._build_request(url)


    def get_balance(self):
        '''
        This will return the user's current balance, in USD.
        '''
        method_path = 'balance/'
        url = os.path.join(self.base_url, method_path)
        return self._build_request(url)


    def make_deposit(self, amount_in_usd, cc_last_four):
        """
        Given a valid CC on file in the app,
        This will depost that amount into the user's balance.
        Note, a credit card may only be added within the app. Not the API.
        """
        method_path = 'payments/deposit/'
        url = os.path.join(self.base_url, method_path)
        data = {
            'AmountInUSD': amount_in_usd,
            'CreditCardLastFourDigits': cc_last_four
        }
        return self._build_request(url, data)

    
    def withdraw_funds(self, amount_in_usd=None):
        """
        Given a PayPal email, this will deposit the funds
        immediately into that user's PayPal account.

        If no amount is specified, it will try and
        deduct the entire user's balance.
        """
        method_path = 'payments/withdraw/'
        url = os.path.join(self.base_url, method_path)
        data = {
            'AmountInUSD': amount_in_usd,
        }
        return self._build_request(url, data)


    def grant_bonus(self, cue_completion_id, amount, reason='Thanks for your hard work!', note_to_self=None):
        """
        This will grant a bonus to the user who has completed
        a particular Cue for us.

        A reason for the bonus must be specified, though here
        we default to "Thanks for your hard work!" if none is provided.

        Note to self can be proviuded, which is a string that can only be viewed
        by the person who granted the bonus. An example might be: 
        "Bonus paid here on 2014-01-01 to see if it motivates better work from this person."
        """
        method_path = 'payments/bonus/'
        url = os.path.join(self.base_url, method_path)
        data = {
            'CueCompletionID': cue_completion_id,
            'Amount': amount,
            'Reason': reason,
            'NoteToSelf': note_to_self
        }
        return self._build_request(url, data)


    def get_payments(self, payment_type=None, payment_id=None, note_to_self=None, page=None):
        """
        Payment type may be one of `Deposits`, `Withdrawals`, or `Bonuses`.
        50 results will show per page.
        """
        method_path = 'payments/'
        url = os.path.join(self.base_url, method_path)
        data = {
            'PaymentType': payment_type,
            'PaymentID': payment_id,
            'NoteToSelf': note_to_self,
            'Page': page
        }
        data = dict((x,y) for x,y in data.items() if y) # dont pass "None" as a string
        if data:
            url = url + '?' + urllib.urlencode(data)
        return self._build_request(url)


    def approve_cue_completion(self, cue_completion_id):
        """
        This will approve a CueCompletion that has been submitted to the user's Cue.
        """
        method_path = 'completions/approve/'
        url = os.path.join(self.base_url, method_path)
        data = {
            'CueCompletionID': cue_completion_id,
        }
        return self._build_request(url, data)


    def decline_cue_completion(self, cue_completion_id):
        """
        This will decline a CueCompletion that has been submitted to the user's Cue.
        """
        method_path = 'completions/decline/'
        url = os.path.join(self.base_url, method_path)
        data = {
            'CueCompletionID': cue_completion_id,
        }
        return self._build_request(url, data)


    def cancel_cue(self, cue_id):
        """
        This will cancel a Cue that you have posted, refunding your balance.
        """
        method_path = 'cues/cancel/'
        url = os.path.join(self.base_url, method_path)
        data = {
            'CueID': cue_id,
        }
        return self._build_request(url, data)


    def get_cue_completions(self, cue_id, cue_completion_id=None, status=None, page=None):
        """
        This will return CueCompletions for a particular Cue.
        Status options for CueCompletions are `Pending`, `Accepted`, and `Declined`.
        """
        method_path = 'completions/'
        url = os.path.join(self.base_url, method_path)
        data = {
            'CueID': cue_id,
            'CueCompletionID': cue_completion_id,
            'Status': status,
            'Page': page,
        }
        data = dict((x,y) for x,y in data.items() if y)
        if data:
            url = url + '?' + urllib.urlencode(data)
        return self._build_request(url)


    def create_cue(self, title, amount, num_opportunities=1,
                   description=None, is_anonymous=None, push_notification_on_cue_completion=None,
                   disallow_anonymous=None, iframe_url=None, url_notification_on_cue_completion=None,
                   email_notification_on_cue_completion=None, limetime_in_minutes=None, 
                   time_limit_to_complete_cue_in_minutes=None, auto_approve_cue_completion_in_minutes=None,
                   note_to_self=None, keywords=None):
        """
        The only required items are `title`, `amount`, and `num_opportunities` (which defaults to 1).
        An `iframe_url` can be specified if you want a user to fill out a custom form on your site.
        """
        method_path = 'cues/create'
        url = os.path.join(self.base_url, method_path)
        data = {
            'Title': title,
            'Amount': amount,
            'NumOpportunities': num_opportunities,
            'Description': description,
            'IsAnonymous': is_anonymous,
            'PushNotificationOnCueCompletion': push_notification_on_cue_completion,
            'DisallowAnonymousCueCompletions': disallow_anonymous,
            'iFrameURL': iframe_url,
            'URLNotificationOnCueCompletion': url_notification_on_cue_completion,
            'EmailNotificationOnCueCompletion': email_notification_on_cue_completion,
            'LifetimeInMinutes': limetime_in_minutes,
            'TimeLimitToCompleteCueInMinutes': time_limit_to_complete_cue_in_minutes,
            'AutoApproveCueCompletionAfterThisManyMinutes': auto_approve_cue_completion_in_minutes,
            'NoteToSelf': note_to_self,
            'Keywords': keywords,
        }
        return self._build_request(url, data)


    def get_cues(self, cue_id=None, group_id=None, note_to_self=None, has_pending_cue_completions=None, status=None, page=None):
        """
        This will get all Cues the user has created.
        `has_pending_cue_completions` is a boolean.
        `status` can be one of 'Active', 'Complete', 'Canceled', or 'Expired'
        """
        method_path = 'cues/'
        url = os.path.join(self.base_url, method_path)
        data = {
            'CueID': cue_id,
            'GroupID': group_id,
            'NoteToSelf': note_to_self,
            'HasPendingCueCompletions': has_pending_cue_completions,
            'Status': status,
            'Page': page,
        }
        data = dict((x,y) for x,y in data.items() if y)
        if data:
            url = url + '?' + urllib.urlencode(data)
        return self._build_request(url)


    def assign_cue(self, cue_id):
        """
        NOTE: This is a Private method.
        This will try and check-in or check-out a Cue depending
        on whether the Cue is already checked out by that user.
        """
        method_path = 'cues/assign/'
        url = os.path.join(self.base_url, method_path)
        data = {
            'CueID': cue_id,
        }
        return self._build_request(url, data)


    def submit_cue_completion(self, assignment_id, answer_text=None, video_url=None, video_thumbnail_url=None, image_url=None, is_anonymous=None):
        """
        NOTE: This is a Private method.
        This will submit the CueCompletion data, though
        In production the method will block any requests without an HTTP_REFERER.
        """
        method_path = 'cues/complete/'
        url = os.path.join(self.base_url, method_path)
        data = {
            'AssignmentID': assignment_id,
            'AnswerText': answer_text,
            'VideoURL': video_url,
            'VideoThumbnailURL': video_thumbnail_url,
            'ImageURL': image_url,
            'IsAnonymous': is_anonymous,
        }
        return self._build_request(url, data)
        





        