from functools import partial
import indicoio.config as config 

JSON_HEADERS = {'Content-type': 'application/json', 'Accept': 'text/plain'}

Version, version, __version__, VERSION = ('0.4.5',) * 4

from indicoio.text.sentiment import political, posneg
from indicoio.text.sentiment import posneg as sentiment
from indicoio.text.lang import language
from indicoio.text.tagging import text_tags
from indicoio.images.fer import fer
from indicoio.images.features import facial_features
from indicoio.images.features import image_features

political = partial(political, config.api_root)
posneg = partial(posneg, config.api_root)
sentiment = partial(sentiment, config.api_root)
posneg = partial(sentiment, config.api_root)
language = partial(language, config.api_root)
fer = partial(fer, config.api_root)
facial_features = partial(facial_features, config.api_root)
image_features = partial(image_features, config.api_root)
text_tags = partial(text_tags, config.api_root)
