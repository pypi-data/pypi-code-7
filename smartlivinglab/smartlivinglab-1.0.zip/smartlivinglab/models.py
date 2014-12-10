from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from rest_framework.authtoken.models import Token

CLUSTERDELTACHOICES = ((0,0),
                       (2,2),
                       (5,5),
                       (10,10),
                       (15,15),
                       (20,20),
                       (30,30),
                       (60, 60),
                       )
                       
class Node(models.Model):
    code = models.CharField(max_length=15,unique=True)
    description = models.TextField()
    lat = models.FloatField()
    lon = models.FloatField()

    def __unicode__(self):
        return self.code
    
class Sensor(models.Model):
    node = models.ForeignKey(Node, related_name='sensors')
    code = models.CharField(max_length=15, unique=True, db_index=True)
    units = models.CharField(max_length=15)
    clusterdeltatime = models.SmallIntegerField(default=0, choices=CLUSTERDELTACHOICES)
    
    def __unicode__(self):
        return self.code + u' in ' + self.node.__unicode__()
    
class Value(models.Model):
    sensor = models.ForeignKey(Sensor,related_name='values')
    value = models.FloatField()
    date = models.DateTimeField()

    def __unicode__(self):
        return unicode(self.value)


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
