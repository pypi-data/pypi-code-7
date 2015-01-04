# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings
import radpress.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=500, editable=False)),
                ('markup', models.CharField(default=b'restructuredtext', max_length=20, choices=[(b'restructuredtext', b'reStructuredText'), (b'markdown', b'Markdown')])),
                ('slug', models.SlugField(unique=True, editable=False)),
                ('content', models.TextField()),
                ('content_body', models.TextField(editable=False)),
                ('is_published', models.BooleanField(editable=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(default=datetime.datetime.now, editable=False)),
                ('author', models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('-created_at', '-updated_at'),
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ArticleTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('article', models.ForeignKey(to='radpress.Article')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EntryImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='A simple description about image.', max_length=100, blank=True)),
                ('image', models.ImageField(upload_to=b'radpress/entry_images/')),
            ],
            options={
                'verbose_name': 'Image',
                'verbose_name_plural': 'Images',
            },
            bases=(radpress.models.ThumbnailModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveSmallIntegerField(default=3)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=500, editable=False)),
                ('markup', models.CharField(default=b'restructuredtext', max_length=20, choices=[(b'restructuredtext', b'reStructuredText'), (b'markdown', b'Markdown')])),
                ('slug', models.SlugField(unique=True, editable=False)),
                ('content', models.TextField()),
                ('content_body', models.TextField(editable=False)),
                ('is_published', models.BooleanField(editable=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(default=datetime.datetime.now, editable=False)),
            ],
            options={
                'ordering': ('-created_at', '-updated_at'),
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='menu',
            name='page',
            field=models.ForeignKey(to='radpress.Page', unique=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='menu',
            unique_together=set([('order', 'page')]),
        ),
        migrations.AddField(
            model_name='articletag',
            name='tag',
            field=models.ForeignKey(to='radpress.Tag'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article',
            name='cover_image',
            field=models.ForeignKey(blank=True, editable=False, to='radpress.EntryImage', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article',
            name='tags',
            field=models.ManyToManyField(to='radpress.Tag', null=True, through='radpress.ArticleTag', blank=True),
            preserve_default=True,
        ),
    ]
