# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteBlock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(unique=True, max_length=255)),
                ('css_class', models.CharField(max_length=255, null=True, blank=True)),
                ('weight', models.IntegerField(default=0, help_text=b'Blocks are displayed in descending order')),
                ('enable_rte', models.BooleanField(default=True, help_text=b'Check this box to use the graphical editor', verbose_name=b'Enable editor')),
                ('data', models.TextField(null=True, blank=True)),
            ],
            options={
                'ordering': ('weight',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SiteMenu',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=255)),
                ('code', models.CharField(max_length=255)),
                ('show_label', models.BooleanField(default=False)),
                ('site', models.ForeignKey(to='sites.Site')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SiteMenuItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=255)),
                ('weight', models.IntegerField(default=0)),
                ('css_class', models.CharField(max_length=255, blank=True)),
            ],
            options={
                'ordering': ['weight'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MenuItemPage',
            fields=[
                ('sitemenuitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='site_content.SiteMenuItem')),
                ('target', models.CharField(max_length=35, blank=True)),
            ],
            options={
            },
            bases=('site_content.sitemenuitem',),
        ),
        migrations.CreateModel(
            name='MenuItemLink',
            fields=[
                ('sitemenuitem_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='site_content.SiteMenuItem')),
                ('url', models.CharField(max_length=255, blank=True)),
                ('target', models.CharField(max_length=35, blank=True)),
            ],
            options={
            },
            bases=('site_content.sitemenuitem',),
        ),
        migrations.CreateModel(
            name='SitePage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(max_length=255)),
                ('title', models.CharField(max_length=255, null=True, blank=True)),
                ('meta_description', models.TextField(null=True, blank=True)),
                ('meta_keywords', models.TextField(null=True, blank=True)),
                ('page_class', models.CharField(max_length=255, null=True, blank=True)),
                ('content_header', models.CharField(max_length=255, null=True, blank=True)),
                ('enable_rte', models.BooleanField(default=True, help_text=b'Check this box to use the graphical editor', verbose_name=b'Enable editor')),
                ('content', models.TextField(null=True, blank=True)),
                ('custom_template', models.CharField(help_text=b'Enter a custom template path. This value will override the template selection dropdown.', max_length=255, null=True, blank=True)),
                ('is_index', models.BooleanField(default=False)),
                ('login_required', models.BooleanField(default=False)),
                ('site', models.ForeignKey(to='sites.Site')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SitePageAlias',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url_alias', models.CharField(help_text=b'Max character length for alias is 255.', unique=True, max_length=255)),
                ('sitepage', models.ForeignKey(to='site_content.SitePage')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SitePagePositionBlock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('weight', models.IntegerField(default=0, help_text=b'Blocks are displayed in descending order')),
                ('siteblocks', models.ForeignKey(to='site_content.SiteBlock')),
                ('sitepage', models.ForeignKey(to='site_content.SitePage')),
            ],
            options={
                'ordering': ('weight',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SitePageRedirect',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(help_text=b'URL to redirect. Max character length for alias is 255.', unique=True, max_length=255)),
                ('sitepage', models.ForeignKey(to='site_content.SitePage')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SitePageTemplateSelection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=255, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('template_path', models.CharField(max_length=255, null=True, blank=True)),
                ('is_system', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SitePosition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(unique=True, max_length=255)),
                ('weight', models.IntegerField(default=0)),
                ('css_class', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='sitepagepositionblock',
            name='siteposition',
            field=models.ForeignKey(to='site_content.SitePosition'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='sitepage',
            name='template',
            field=models.ForeignKey(blank=True, to='site_content.SitePageTemplateSelection', null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='sitepage',
            unique_together=set([('site', 'url')]),
        ),
        migrations.AddField(
            model_name='sitemenuitem',
            name='sitemenu',
            field=models.ForeignKey(related_name=b'sitemenu', to='site_content.SiteMenu'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='sitemenuitem',
            name='submenu',
            field=models.ForeignKey(related_name=b'submenu', blank=True, to='site_content.SiteMenu', null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='sitemenu',
            unique_together=set([('site', 'code')]),
        ),
        migrations.AddField(
            model_name='siteblock',
            name='siteposition',
            field=models.ForeignKey(blank=True, to='site_content.SitePosition', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='menuitempage',
            name='page',
            field=models.ForeignKey(to='site_content.SitePage'),
            preserve_default=True,
        ),
    ]
