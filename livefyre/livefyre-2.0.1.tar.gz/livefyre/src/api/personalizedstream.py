import requests, jwt

from livefyre.src.api.domain import Domain
from livefyre.src.dto.topic import Topic
from livefyre.src.dto.subscription import Subscription, SubscriptionType
from livefyre.src.exceptions import ApiException
from livefyre.src.utils import get_network_from_core, pyver

try:
    import simplejson as json
except ImportError:
    import json


def get_url(core):
    return PersonalizedStream.BASE_URL.format(Domain.quill(core))

def get_lf_token_header(core, user_token=None):
    return {
            'Authorization': 'lftoken ' + (get_network_from_core(core).build_livefyre_token() if user_token is None else user_token),
            'Accepts': 'application/json'
    }
    
def evaluate_response(response):
    if response.status_code >= 400:
        raise ApiException(response.status_code)
    return response.json()

    
class PersonalizedStream(object):
    BASE_URL = '{0}/api/v4'
    STREAM_BASE_URL = '{0}/api/v4'
    
    TOPIC_PATH = '/{0}/'
    MULTIPLE_TOPIC_PATH = '/{0}:topics/';
    USER_SUBSCRIPTION_PATH = '/{0}:subscriptions/';
    TOPIC_SUBSCRIPTION_PATH = '/{0}:subscribers/';
    TIMELINE_PATH = '/timeline/';
    
    @staticmethod
    def get_topic(core, topic_id):
        url = get_url(core) + PersonalizedStream.TOPIC_PATH.format(Topic.generate_urn(core, topic_id))
        headers = get_lf_token_header(core)

        response = requests.get(url, headers = headers)
        data = evaluate_response(response)['data']
        
        return Topic.serialize_from_json(data['topic']) if 'topic' in data else None

    @staticmethod
    def create_or_update_topic(core, topic_id, label):
        return PersonalizedStream.create_or_update_topics(core, { topic_id: label })[0]
    
    @staticmethod
    def delete_topic(core, topic):
        return PersonalizedStream.delete_topics(core, [topic]) == 1

    @staticmethod
    def get_topics(core, limit=100, offset=0):
        url = get_url(core) + PersonalizedStream.MULTIPLE_TOPIC_PATH.format(core.urn)
        headers = get_lf_token_header(core)

        response = requests.get(url, params = {'limit': limit, 'offset': offset}, headers = headers)
        data = evaluate_response(response)['data']

        return [Topic.serialize_from_json(x) for x in data['topics']] if 'topics' in data else []

    @staticmethod
    def create_or_update_topics(core, topic_map):
        topics = []
        if pyver < 3.0:
            topics = [Topic.create(core, k, v) for k, v in topic_map.iteritems()]
        else:
            topics = [Topic.create(core, k, v) for k, v in topic_map.items()]
        
        for topic in topics:
            assert topic.label and len(topic.label) <= 128, 'topic label should not be empty and have 128 or less characters'
        
        url = get_url(core) + PersonalizedStream.MULTIPLE_TOPIC_PATH.format(core.urn)
        form = json.dumps({'topics': [x.to_dict() for x in topics]})
        headers = get_lf_token_header(core)
        headers['Content-Type'] = 'application/json'
        
        response = requests.post(url, data = form, headers = headers)
        evaluate_response(response)['data']
        
        return topics
        
    @staticmethod
    def delete_topics(core, topics):
        url = get_url(core) + PersonalizedStream.MULTIPLE_TOPIC_PATH.format(core.urn)
        form = json.dumps({'delete': [x.topic_id for x in topics]})
        headers = get_lf_token_header(core)
        headers['Content-Type'] = 'application/json'
        
        response = requests.patch(url, data = form, headers = headers)
        data = evaluate_response(response)['data']
        
        return data['deleted'] if 'deleted' in data else 0
    
    @staticmethod
    def get_collection_topics(collection):
        url = get_url(collection) + PersonalizedStream.MULTIPLE_TOPIC_PATH.format(collection.urn)
        headers = get_lf_token_header(collection)

        response = requests.get(url, headers = headers)
        data = evaluate_response(response)['data']
        
        return data['topicIds'] if 'topicIds' in data else []

    @staticmethod
    def add_collection_topics(collection, topics):
        url = get_url(collection) + PersonalizedStream.MULTIPLE_TOPIC_PATH.format(collection.urn)
        form = json.dumps({'topicIds': [x.topic_id for x in topics]})
        headers = get_lf_token_header(collection)
        headers['Content-Type'] = 'application/json'
        
        response = requests.post(url, data = form, headers = headers)
        data = evaluate_response(response)['data']
        
        return data['added'] if 'added' in data else 0
    
    @staticmethod
    def replace_collection_topics(collection, topics):
        url = get_url(collection) + PersonalizedStream.MULTIPLE_TOPIC_PATH.format(collection.urn)
        form = json.dumps({'topicIds': [x.topic_id for x in topics]})
        headers = get_lf_token_header(collection)
        headers['Content-Type'] = 'application/json'
        
        response = requests.put(url, data = form, headers = headers)
        data = evaluate_response(response)['data']
        
        added = data['added'] if 'added' in data else 0
        removed = data['removed'] if 'removed' in data else 0
        
        return added, removed
        
    @staticmethod
    def remove_collection_topics(collection, topics):
        url = get_url(collection) + PersonalizedStream.MULTIPLE_TOPIC_PATH.format(collection.urn)
        form = json.dumps({'delete': [x.topic_id for x in topics]})
        headers = get_lf_token_header(collection)
        headers['Content-Type'] = 'application/json'
        
        response = requests.patch(url, data = form, headers = headers)
        data = evaluate_response(response)['data']
        
        return data['removed'] if 'removed' in data else 0
    
    @staticmethod
    def get_subscriptions(network, user_id):
        url = get_url(network) + PersonalizedStream.USER_SUBSCRIPTION_PATH.format(network.get_urn_for_user(user_id))
        headers = get_lf_token_header(network)

        response = requests.get(url, headers = headers)
        data = evaluate_response(response)['data']
        
        return [Subscription.serialize_from_json(x) for x in data['subscriptions']] if 'subscriptions' in data else []

    @staticmethod
    def add_subscriptions(network, user_token, topics):
        user_id = jwt.decode(user_token, network.data.key)['user_id']
        user_urn = network.get_urn_for_user(user_id)
        url = get_url(network) + PersonalizedStream.USER_SUBSCRIPTION_PATH.format(user_urn)
        form = json.dumps({'subscriptions': [Subscription(x.topic_id, user_urn, SubscriptionType.personalStream) for x in topics]})
        headers = get_lf_token_header(network, user_token)
        headers['Content-Type'] = 'application/json'
        
        response = requests.post(url, data = form, headers = headers)
        data = evaluate_response(response)['data']
        
        return data['added'] if 'added' in data else 0
    
    @staticmethod
    def replace_subscriptions(network, user_token, topics):
        user_id = jwt.decode(user_token, network.data.key)['user_id']
        user_urn = network.get_urn_for_user(user_id)
        url = get_url(network) + PersonalizedStream.USER_SUBSCRIPTION_PATH.format(user_urn)
        form = json.dumps({'subscriptions': [Subscription(x.topic_id, user_urn, SubscriptionType.personalStream) for x in topics]})
        headers = get_lf_token_header(network, user_token)
        headers['Content-Type'] = 'application/json'
        
        response = requests.put(url, data = form, headers = headers)
        data = evaluate_response(response)['data']
        
        added = data['added'] if 'added' in data else 0
        removed = data['removed'] if 'removed' in data else 0
            
        return added, removed
        
    @staticmethod
    def remove_subscriptions(network, user_token, topics):
        user_id = jwt.decode(user_token, network.data.key)['user_id']
        user_urn = network.get_urn_for_user(user_id)
        url = get_url(network) + PersonalizedStream.USER_SUBSCRIPTION_PATH.format(user_urn)
        form = json.dumps({'delete': [Subscription(x.topic_id, user_urn, SubscriptionType.personalStream) for x in topics]})
        headers = get_lf_token_header(network, user_token)
        headers['Content-Type'] = 'application/json'
        
        response = requests.patch(url, data = form, headers = headers)
        data = evaluate_response(response)['data']
    
        return data['removed'] if 'removed' in data else 0
    
    @staticmethod
    def get_subscribers(network, topic, limit=100, offset=0):
        url = get_url(network) + PersonalizedStream.TOPIC_SUBSCRIPTION_PATH.format(topic.topic_id)
        headers = get_lf_token_header(network)

        response = requests.get(url, params = {'limit': limit, 'offset': offset}, headers = headers)
        data = evaluate_response(response)['data']
        
        return [Subscription.serialize_from_json(x) for x in data['subscriptions']] if 'subscriptions' in data else []
    
    @staticmethod
    def get_timeline_stream(cursor, is_next):
        url = PersonalizedStream.STREAM_BASE_URL.format(Domain.bootstrap(cursor.core)) + PersonalizedStream.TIMELINE_PATH
        headers = get_lf_token_header(cursor.core)
        params = {'resource': cursor.data.resource, 'limit': cursor.data.limit}
        
        if is_next:
            params['since'] = cursor.data.cursor_time
        else:
            params['until'] = cursor.data.cursor_time

        response = requests.get(url, params = params, headers = headers)
        return evaluate_response(response)
    