# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BitBucketRepo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now)),
                ('name', models.CharField(help_text='Name of the repo. Used for internal identification', max_length=100)),
                ('slug', models.SlugField(help_text='Slug ID given by BitBucket for this repository.', max_length=100)),
                ('access_key', models.CharField(help_text='Secret key used to "authenticate" the request. If saved here the key must be appended to the BitBucket hook URL like so: http://yourserver.com/broker/?access_key=YOUR_ACCESS_KEY', max_length=100, blank=True)),
            ],
            options={
                'verbose_name': 'BitBucket Repository',
                'verbose_name_plural': 'BitBucket Repositories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BitBucketRule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now)),
                ('action', models.PositiveIntegerField(choices=[(1, 'Referenced'), (2, 'Fixes / Closes')])),
                ('update', models.BooleanField(default=True, help_text='If checked, card will be updated with commit comment.')),
                ('archive', models.BooleanField(default=False, help_text='If checked, card will be archived.')),
                ('move', models.BooleanField(default=False, help_text='If checked, card will be moved to specified Trello List.')),
                ('repo', models.ForeignKey(related_name='rules', to='trello_broker.BitBucketRepo')),
            ],
            options={
                'verbose_name': 'BitBucket Rule',
                'verbose_name_plural': 'BitBucket Rules',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TrelloBoard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now)),
                ('name', models.CharField(max_length=100, blank=True)),
                ('status', models.PositiveIntegerField(default=0, choices=[(0, 'Active'), (1, 'Archived')])),
                ('trello_id', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Trello Board',
                'verbose_name_plural': 'Trello Boards',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TrelloList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now)),
                ('name', models.CharField(max_length=100)),
                ('status', models.PositiveIntegerField(default=0, choices=[(0, 'Active'), (1, 'Archived')])),
                ('trello_id', models.CharField(max_length=100)),
                ('trello_board', models.ForeignKey(related_name='trello_lists', to='trello_broker.TrelloBoard')),
            ],
            options={
                'verbose_name': 'Trello List',
                'verbose_name_plural': 'Trello Lists',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TrelloToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now)),
                ('name', models.CharField(help_text='Name of the account. Used for internal identification', max_length=100)),
                ('api_key', models.CharField(help_text='Get this from https://trello.com/1/appKey/generate', max_length=100)),
                ('api_token', models.CharField(help_text='Get this from https://trello.com/1/authorize?key=YOUR_API_KEY&name=Your+App+Name&expiration=never&response_type=token&scope=read,write', max_length=100)),
            ],
            options={
                'verbose_name': 'Trello Token',
                'verbose_name_plural': 'Trello Tokens',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='trelloboard',
            name='trello_token',
            field=models.ForeignKey(to='trello_broker.TrelloToken'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bitbucketrule',
            name='trello_list',
            field=models.ForeignKey(blank=True, to='trello_broker.TrelloList', null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='bitbucketrule',
            unique_together=set([('repo', 'action')]),
        ),
        migrations.AddField(
            model_name='bitbucketrepo',
            name='trello_board',
            field=models.ForeignKey(related_name='repos', to='trello_broker.TrelloBoard'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='bitbucketrepo',
            unique_together=set([('slug', 'access_key')]),
        ),
    ]
