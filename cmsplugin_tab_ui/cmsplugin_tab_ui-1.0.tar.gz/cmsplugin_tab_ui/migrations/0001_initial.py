# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import paintstore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0003_auto_20140926_2347'),
    ]

    operations = [
        migrations.CreateModel(
            name='TabUi',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('title', models.CharField(max_length=255)),
                ('title_color', paintstore.fields.ColorPickerField(max_length=7, null=True, blank=True)),
                ('background_color', paintstore.fields.ColorPickerField(max_length=7, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='TabUiList',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('custom_classes', models.CharField(max_length=200, verbose_name='custom classes', blank=True)),
                ('align', models.CharField(default=b'h', max_length=1, choices=[(b'v', 'Vertical'), (b'h', 'Horizontal')])),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
