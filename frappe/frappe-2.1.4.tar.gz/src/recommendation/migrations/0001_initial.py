# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import recommendation.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_dropped', models.BooleanField(default=False, verbose_name='is dropped')),
            ],
            options={
                'verbose_name': 'owned item',
                'verbose_name_plural': 'owned items',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('external_id', models.CharField(unique=True, max_length=255, verbose_name='external id')),
            ],
            options={
                'verbose_name': 'item',
                'verbose_name_plural': 'items',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Matrix',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('model_id', models.SmallIntegerField(null=True, verbose_name='model id', blank=True)),
                ('numpy', recommendation.models.NPArrayField(verbose_name='numpy array')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='timestamp')),
            ],
            options={
                'verbose_name': 'matrix',
                'verbose_name_plural': 'matrix',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('external_id', models.CharField(unique=True, max_length=255, verbose_name='external id')),
                ('items', models.ManyToManyField(to='recommendation.Item', verbose_name='items', through='recommendation.Inventory', blank=True)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='inventory',
            name='item',
            field=models.ForeignKey(verbose_name='item', to='recommendation.Item'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='inventory',
            name='user',
            field=models.ForeignKey(verbose_name='user', to='recommendation.User'),
            preserve_default=True,
        ),
    ]
