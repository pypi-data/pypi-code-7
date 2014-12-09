# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('PeerReviewApp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReviewFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('filename', models.CharField(max_length=255)),
                ('upload', models.FileField(null=True, upload_to=b'reviewdocs/%Y/%m/%d', blank=True)),
                ('manuscript', models.ForeignKey(related_query_name=b'reviewdoc', related_name=b'reviewdocs', to='PeerReviewApp.Manuscript')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RenameField(
            model_name='manuscriptfile',
            old_name='name',
            new_name='filename',
        ),
        migrations.AlterField(
            model_name='manuscript',
            name='status',
            field=models.CharField(default=b'Saved', max_length=20),
        ),
        migrations.AlterField(
            model_name='reviewperiod',
            name='start_date',
            field=models.DateField(default=datetime.datetime(2014, 12, 2, 13, 14, 10, 501547)),
        ),
    ]
