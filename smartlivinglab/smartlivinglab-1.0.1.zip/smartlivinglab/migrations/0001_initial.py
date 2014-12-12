# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(unique=True, max_length=15)),
                ('description', models.TextField()),
                ('lat', models.FloatField()),
                ('lon', models.FloatField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(unique=True, max_length=15, db_index=True)),
                ('units', models.CharField(max_length=15)),
                ('node', models.ForeignKey(related_name='sensors', to='smartlivinglab.Node')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Value',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.FloatField()),
                ('date', models.DateTimeField()),
                ('sensor', models.ForeignKey(related_name='values', to='smartlivinglab.Sensor')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
