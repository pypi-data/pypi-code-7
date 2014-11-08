from functools import partial
import indicoio.config as config

JSON_HEADERS = {'Content-type': 'application/json', 'Accept': 'text/plain'}

from indicoio.text.sentiment import political, posneg
from indicoio.text.sentiment import posneg as sentiment
from indicoio.text.lang import language
from indicoio.text.tagging import text_tags
from indicoio.images.fer import fer
from indicoio.images.features import facial_features
from indicoio.images.features import image_features

political = partial(political, config.local_api_root)
posneg = partial(posneg, config.local_api_root)
sentiment = partial(sentiment, config.local_api_root)
posneg = partial(sentiment, config.local_api_root)
language = partial(language, config.local_api_root)
fer = partial(fer, config.local_api_root)
facial_features = partial(facial_features, config.local_api_root)
image_features = partial(image_features, config.local_api_root)
text_tags = partial(text_tags, config.local_api_root)
