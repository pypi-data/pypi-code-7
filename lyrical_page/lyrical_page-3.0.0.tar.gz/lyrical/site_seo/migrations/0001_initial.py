# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        ('site_content', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteUrl',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(max_length=255)),
                ('page_title', models.TextField(null=True, blank=True)),
                ('page_keywords', models.TextField(null=True, blank=True)),
                ('page_description', models.TextField(null=True, blank=True)),
                ('site', models.ForeignKey(to='sites.Site')),
                ('sitepages', models.ManyToManyField(to='site_content.SitePage', null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SiteUrl404',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.TextField(null=True, blank=True)),
                ('date_created', models.DateTimeField(default=datetime.datetime.now)),
                ('date_list_hit', models.DateTimeField(default=datetime.datetime.now, auto_now=True)),
                ('hit_cnt', models.IntegerField(default=0)),
                ('site', models.ForeignKey(to='sites.Site')),
            ],
            options={
                'ordering': ('url',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SiteUrlDefaults',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('page_title', models.TextField(null=True, blank=True)),
                ('page_keywords', models.TextField(null=True, blank=True)),
                ('page_description', models.TextField(null=True, blank=True)),
                ('site', models.ForeignKey(to='sites.Site')),
            ],
            options={
                'verbose_name_plural': 'site url defaults',
            },
            bases=(models.Model,),
        ),
    ]
