# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('geoprisma', '0001_initial'),
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'Action',
                'verbose_name_plural': 'Actions',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Right',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('actions', models.ManyToManyField(to='acl.Action')),
                ('id_group', models.ForeignKey(to='auth.Group')),
                ('id_resource', models.ForeignKey(to='geoprisma.Resource')),
            ],
            options={
                'ordering': ('id_group', 'id_resource'),
                'verbose_name': 'Right',
                'verbose_name_plural': 'Rights',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='right',
            unique_together=set([('id_group', 'id_resource')]),
        ),
    ]
