# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Advertiser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('company_name', models.CharField(max_length=150, verbose_name='Company Name')),
                ('website', models.URLField(null=True, verbose_name='Company Website', blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('company_name',),
                'abstract': False,
                'verbose_name': 'Advertiser',
                'verbose_name_plural': 'Advertisers',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BannerAdvertisement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=150, verbose_name='Title')),
                ('status', models.IntegerField(default=0, choices=[(0, b'Draft'), (0, b'Published')])),
                ('publish_on', models.DateTimeField(null=True, verbose_name='Publish On', blank=True)),
                ('publish_until', models.DateTimeField(null=True, verbose_name='Published Until', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('content', models.ImageField(upload_to=b'advertisements/banner')),
                ('advertiser', models.ForeignKey(to='advert.Advertiser')),
            ],
            options={
                'verbose_name': 'Banner Advertisement',
                'verbose_name_plural': 'Banner Advertisements',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TextAdvertisement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=150, verbose_name='Title')),
                ('status', models.IntegerField(default=0, choices=[(0, b'Draft'), (0, b'Published')])),
                ('publish_on', models.DateTimeField(null=True, verbose_name='Publish On', blank=True)),
                ('publish_until', models.DateTimeField(null=True, verbose_name='Published Until', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('content', models.TextField()),
                ('advertiser', models.ForeignKey(to='advert.Advertiser')),
            ],
            options={
                'verbose_name': 'Text Advertisement',
                'verbose_name_plural': 'Text Advertisements',
            },
            bases=(models.Model,),
        ),
    ]
