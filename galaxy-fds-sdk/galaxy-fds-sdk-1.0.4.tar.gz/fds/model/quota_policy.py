
class QuotaPolicy(object):
    @staticmethod
    def get_quota_policy(response_content):
        quota = []
        if response_content != '':
            if 'QPS' in response_content.keys():
                quota.qps = response_content['QPS']
            if 'ThroughPut' in response_content.keys():
                quota.thoughPut = response_content['ThoughPut']
            return quota
        return None