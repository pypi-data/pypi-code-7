from django.db import models
import datetime

class ContactForm(models.Model):
    Nama = models.CharField(max_length=50)
    Email = models.EmailField(max_length=100)
    Tanggal = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now)

    def __unicode__(self):
        return self.Email

class Meta:
    ordering = ['-Tanggal']