# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TemplateFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Template name, for example, "headline"', max_length=255, verbose_name='Template name')),
                ('weight', models.IntegerField(default=0, verbose_name='Output order')),
                ('template_filename', models.CharField(max_length=500, verbose_name='Template file name', blank=True)),
                ('use_content', models.BooleanField(default=False, verbose_name='Use template text')),
                ('template_content', models.TextField(verbose_name='Template text', blank=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('only_for_superuser', models.BooleanField(default=False, verbose_name='Only for superuser')),
            ],
            options={
                'ordering': ['weight'],
                'verbose_name': 'Template file',
                'verbose_name_plural': 'Template files',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TemplateZone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Zone name')),
                ('description', models.TextField(verbose_name='Short description', blank=True)),
            ],
            options={
                'verbose_name': 'Template zone',
                'verbose_name_plural': 'Template zones',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='templatefile',
            name='zone',
            field=models.ForeignKey(related_name=b'files', verbose_name='Zone', to='cmstemplates.TemplateZone'),
            preserve_default=True,
        ),
    ]
