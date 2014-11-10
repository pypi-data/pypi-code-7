# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AccessFilter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('commentaire', models.TextField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AccessFilterOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('value', models.TextField(null=True, blank=True)),
                ('accessfilter', models.ForeignKey(to='geoprisma.AccessFilter')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('template', models.CharField(default=b'', max_length=255)),
                ('commentaire', models.TextField(null=True, blank=True)),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ApplicationType',
            fields=[
                ('id', models.IntegerField(unique=True, serialize=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('activated', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ApplicationWidget',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField(null=True, blank=True)),
                ('application', models.ForeignKey(to='geoprisma.Application')),
            ],
            options={
                'ordering': ('order',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Datastore',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('layers', models.CharField(max_length=255, null=True)),
                ('commentaire', models.TextField(null=True, blank=True)),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DatastoreOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('value', models.TextField(null=True, blank=True)),
                ('datastore', models.ForeignKey(to='geoprisma.Datastore')),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DefaultLayerOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('value', models.TextField(null=True, blank=True)),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Field',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('title', models.CharField(max_length=255, blank=True)),
                ('key', models.CharField(max_length=255, null=True, blank=True)),
                ('domain', models.CharField(max_length=255, null=True, blank=True)),
                ('commentaire', models.TextField(null=True, blank=True)),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FieldOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('value', models.TextField(null=True, blank=True)),
                ('field', models.ForeignKey(to='geoprisma.Field')),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='InitialView',
            fields=[
                ('id_initial_view', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=100)),
                ('geom', django.contrib.gis.db.models.fields.GeometryField(srid=32187)),
                ('sort_index', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MapContext',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('commentaire', models.TextField(null=True, blank=True)),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MapContextOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('value', models.TextField(null=True, blank=True)),
                ('mapContext', models.ForeignKey(to='geoprisma.MapContext', db_column=b'mapcontext_id')),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MapContextResource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField(null=True, blank=True)),
                ('mapContext', models.ForeignKey(to='geoprisma.MapContext', db_column=b'mapcontext_id')),
            ],
            options={
                'ordering': ('order',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('acl_name', models.CharField(max_length=255, null=True, db_column=b'acl_name', blank=True)),
                ('key', models.CharField(max_length=255, null=True, blank=True)),
                ('domain', models.CharField(max_length=255, null=True, blank=True)),
                ('slug', models.SlugField(max_length=255, unique=True, null=True)),
                ('display_name', models.CharField(max_length=255, null=True, blank=True)),
                ('display_name_fr', models.CharField(max_length=255, null=True, blank=True)),
                ('commentaire', models.TextField()),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResourceAccessfilter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('accessfilter', models.ForeignKey(to='geoprisma.AccessFilter')),
                ('resource', models.ForeignKey(to='geoprisma.Resource')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResourceField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField(null=True, blank=True)),
                ('field', models.ForeignKey(to='geoprisma.Field')),
                ('resource', models.ForeignKey(to='geoprisma.Resource')),
            ],
            options={
                'ordering': ('order',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ResourceOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('value', models.TextField(null=True, blank=True)),
                ('key', models.CharField(max_length=255, null=True, blank=True)),
                ('domain', models.CharField(max_length=255, null=True, blank=True)),
                ('resource', models.ForeignKey(to='geoprisma.Resource')),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('source', models.CharField(max_length=1024)),
                ('slug', models.SlugField(max_length=255, unique=True, null=True)),
                ('commentaire', models.TextField(null=True, blank=True)),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServiceOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('value', models.TextField(null=True, blank=True)),
                ('service', models.ForeignKey(to='geoprisma.Service')),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServiceType',
            fields=[
                ('id', models.IntegerField(unique=True, serialize=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('activated', models.BooleanField(default=True)),
                ('priority', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('commentaire', models.TextField(null=True, blank=True)),
                ('application', models.ForeignKey(to='geoprisma.Application')),
                ('mapContext', models.ForeignKey(to='geoprisma.MapContext', db_column=b'mapcontext_id')),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Widget',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('commentaire', models.TextField()),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WidgetOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('value', models.TextField(null=True, blank=True)),
                ('order', models.IntegerField(null=True, blank=True)),
                ('widget', models.ForeignKey(to='geoprisma.Widget')),
            ],
            options={
                'ordering': ('order',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WidgetType',
            fields=[
                ('id', models.IntegerField(unique=True, serialize=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('activated', models.BooleanField(default=True)),
                ('classname', models.CharField(default=b'geoprisma.core.widgets.widgetbase.WidgetBase', max_length=255)),
                ('action', models.CharField(default=b'read', max_length=255)),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='widget',
            name='type',
            field=models.ForeignKey(to='geoprisma.WidgetType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='type',
            field=models.ForeignKey(to='geoprisma.ServiceType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resource',
            name='accessfilters',
            field=models.ManyToManyField(to='geoprisma.AccessFilter', null=True, through='geoprisma.ResourceAccessfilter', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resource',
            name='datastores',
            field=models.ManyToManyField(to='geoprisma.Datastore', db_table=b'geoprisma_resourcedatastore'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='resource',
            name='fields',
            field=models.ManyToManyField(to='geoprisma.Field', through='geoprisma.ResourceField'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mapcontextresource',
            name='resource',
            field=models.ForeignKey(to='geoprisma.Resource'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mapcontext',
            name='resources',
            field=models.ManyToManyField(to='geoprisma.Resource', through='geoprisma.MapContextResource'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='initialview',
            name='id_session',
            field=models.ForeignKey(to='geoprisma.Session'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='defaultlayeroption',
            name='servicetype',
            field=models.ForeignKey(to='geoprisma.ServiceType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='datastore',
            name='service',
            field=models.ForeignKey(to='geoprisma.Service'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='applicationwidget',
            name='widget',
            field=models.ForeignKey(to='geoprisma.Widget'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='application',
            name='type',
            field=models.ForeignKey(to='geoprisma.ApplicationType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='application',
            name='widgets',
            field=models.ManyToManyField(to='geoprisma.Widget', through='geoprisma.ApplicationWidget'),
            preserve_default=True,
        ),
    ]
