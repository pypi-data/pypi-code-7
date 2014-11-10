from time import strftime,gmtime,time
import urllib2
import hmac
import hashlib
import base64
import string
from settings import AWS_CREDS_PATH, AWS_ZONE
import boto.ses


def get_creds():
    f = open(AWS_CREDS_PATH, "r")

    access_key, priv_key = f.readlines()
    return access_key[:-2], priv_key[:-2]


def ses_send_email(subject, topic_arn, msg):
    ak, pk = get_creds()
    conn = boto.ses.connect_to_region(
        AWS_ZONE,
        aws_access_key_id=ak,
        aws_secret_access_key=pk)
    conn.send_email(
        'jpardo@digitalhigh.es',
        'Your subject',
        'Body here',
        ['pardobj@gmail.com'])

def publish_amazon_sns_msg(Subject, TopicArn, Message):
    #http://docs.amazonwebservices.com/AWSSimpleQueueService/2008-01-01/SQSDeveloperGuide/
    ak, pk = get_creds()
    amzsnshost = AWS_HOST
    params = {'Subject': Subject,
            'TopicArn': TopicArn,
            'Message': Message,
            'Timestamp': strftime("%Y-%m-%dT%H:%M:%S.000Z", gmtime(time())),
            'AWSAccessKeyId': ak,
            'Action': 'Publish',
            'SignatureVersion': '2',
            'SignatureMethod': 'HmacSHA256',
            }

    cannqs = string.join(["%s=%s" % (urllib2.quote(key), urllib2.quote(params[key], safe='-_~')) for key in sorted(params.keys())], '&')
    string_to_sign = string.join(["GET", amzsnshost, "/", cannqs], '\n')
    sig = base64.b64encode(hmac.new(pk,string_to_sign,digestmod=hashlib.sha256).digest())
    url = "http://%s/?%s&Signature=%s" % (amzsnshost, cannqs, urllib2.quote(sig))

    try:
        return urllib2.urlopen(url).read()
    except urllib2.HTTPError as  exception:
        return "Error %s (%s):\n%s"%(exception.code,exception.msg,exception.read())
