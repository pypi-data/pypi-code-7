# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('is_deleted', models.BooleanField(default=False)),
                ('iso', models.CharField(max_length=2, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=128)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EnvironmentalTheme',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('title', models.CharField(max_length=128)),
            ],
            options={
                'ordering': ('-pk',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GeographicalScope',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('title', models.CharField(max_length=128)),
                ('require_country', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('-pk',),
            },
            bases=(models.Model,),
        ),
    ]
