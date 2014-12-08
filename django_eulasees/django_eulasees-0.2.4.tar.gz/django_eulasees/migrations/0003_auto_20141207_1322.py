# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_eulasees', '0002_auto_20141206_1419'),
    ]

    operations = [
        migrations.CreateModel(
            name='TagEula',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('eula', models.ForeignKey(to='django_eulasees.RawEula')),
                ('tag', models.ForeignKey(to='django_eulasees.Tag')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TagIcon',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('icon', models.CharField(max_length=200)),
                ('tag', models.ForeignKey(to='django_eulasees.Tag')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.DeleteModel(
            name='SnippetData',
        ),
        migrations.RemoveField(
            model_name='eulasnippet',
            name='end',
        ),
        migrations.RemoveField(
            model_name='eulasnippet',
            name='start',
        ),
    ]
