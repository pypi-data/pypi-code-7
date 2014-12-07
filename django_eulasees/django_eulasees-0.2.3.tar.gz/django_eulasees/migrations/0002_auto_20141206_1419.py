# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_eulasees', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='snippettag',
            name='snippet',
            field=models.ForeignKey(default=0, to='django_eulasees.EulaSnippet'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='snippettag',
            name='tag',
            field=models.ForeignKey(to='django_eulasees.Tag'),
            preserve_default=True,
        ),
    ]
