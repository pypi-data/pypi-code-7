# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('PeerReviewApp', '0002_auto_20141202_1314'),
    ]

    operations = [
        migrations.AddField(
            model_name='reviewperiod',
            name='group_meeting_venue',
            field=models.CharField(default=b'None', max_length=1000),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='reviewperiod',
            name='is_current',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='reviewperiod',
            name='max_manuscript',
            field=models.IntegerField(default=10),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='siteuser',
            name='is_site_admin',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='siteuser',
            name='research_interest',
            field=models.CharField(default=b'None', help_text=b'Research interests, separated by a comma', max_length=200),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='reviewperiod',
            name='start_date',
            field=models.DateField(default=datetime.datetime(2014, 12, 2, 14, 37, 59, 290900)),
        ),
    ]
