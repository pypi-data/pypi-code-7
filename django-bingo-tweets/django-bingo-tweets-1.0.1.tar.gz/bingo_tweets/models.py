from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils.translation import ugettext as _

import tweepy

from bingo.models import Game

TWITTER_API_KEY = getattr(settings, "TWITTER_API_KEY", None)
TWITTER_API_SECRET = getattr(settings, "TWITTER_API_SECRET", None)
TWITTER_ACCESS_TOKEN = getattr(settings, "TWITTER_ACCESS_TOKEN", None)
TWITTER_ACCESS_TOKEN_SECRET = getattr(
    settings,
    "TWITTER_ACCESS_TOKEN_SECRET", None)
TWEET_TEXT = getattr(settings, "TWEET_TEXT",
    _("New game: http://{domain:s}{absolute_url:s}"))
TWEET_TEXT_WITH_TOPIC = getattr(settings, "TWEET_TEXT_WITH_TOPIC",
    _("New game: http://{domain:s}{absolute_url:s} (Topic: {topic:s})"))


@receiver(post_save, sender=Game)
def tweet_game(sender, instance, created, **kwargs):
    game = instance
    if created and TWITTER_API_KEY and TWITTER_API_SECRET and \
       TWITTER_ACCESS_TOKEN and TWITTER_ACCESS_TOKEN_SECRET:
        auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
        auth.set_access_token(TWITTER_ACCESS_TOKEN,
                              TWITTER_ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth)
        if game.description:
            tweet = unicode(TWEET_TEXT_WITH_TOPIC, "utf-8").format(
                domain=game.site.domain,
                absolute_url=game.get_absolute_url(),
                topic=game.description)
        else:
            tweet = unicode(TWEET_TEXT, "utf-8").format(
                domain=game.site.domain,
                absolute_url=game.get_absolute_url())
        api.update_status(tweet)
