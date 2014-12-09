# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('PeerReviewApp', '0003_auto_20141202_1437'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manuscript',
            name='keywords',
            field=models.CharField(help_text=b'Keywords, separated by a comma', max_length=1000),
        ),
        migrations.AlterField(
            model_name='reviewperiod',
            name='start_date',
            field=models.DateField(default=datetime.datetime(2014, 12, 2, 14, 57, 5, 296912)),
        ),
    ]
