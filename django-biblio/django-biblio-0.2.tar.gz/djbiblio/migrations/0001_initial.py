# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djbiblio.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Bibtag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tag', models.CharField(max_length=20, verbose_name=b'Field Name')),
                ('value', models.TextField(max_length=1000)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=120)),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Work',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mnemonic', models.CharField(max_length=120)),
                ('slug', models.SlugField(unique=True)),
                ('abstract', models.TextField(max_length=2000, blank=True)),
                ('workurl', models.URLField(verbose_name=b"Work's URL")),
                ('upload', djbiblio.models.WorkFileField(upload_to=djbiblio.models.upload_work_inst, blank=True)),
                ('projects', models.ManyToManyField(related_name='works', to='djbiblio.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='bibtag',
            name='work',
            field=models.ForeignKey(related_name='bibtags', to='djbiblio.Work'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='bibtag',
            unique_together=set([('tag', 'work')]),
        ),
        migrations.AddField(
            model_name='author',
            name='works',
            field=models.ManyToManyField(related_name='authors', to='djbiblio.Work'),
            preserve_default=True,
        ),
    ]
