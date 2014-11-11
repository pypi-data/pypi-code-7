# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('payload', models.TextField()),
                ('user', models.CharField(max_length=200)),
                ('status', models.BooleanField(default=False)),
                ('status_message', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('skip', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('-created',),
                'db_table': 'ftp_deploy_log',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200)),
                ('success', models.TextField(blank=True)),
                ('fail', models.TextField(blank=True)),
                ('commit_user', models.CharField(max_length=50, verbose_name=b'Commit User', blank=True)),
                ('deploy_user', models.CharField(max_length=50, verbose_name=b'Deploy User', blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ('name',),
                'db_table': 'ftp_deploy_notification',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ftp_host', models.CharField(max_length=255, verbose_name=b'Host')),
                ('ftp_username', models.CharField(max_length=50, verbose_name=b'Username')),
                ('ftp_password', models.CharField(max_length=50, verbose_name=b'Password')),
                ('ftp_path', models.CharField(max_length=255, verbose_name=b'Path')),
                ('repo_source', models.CharField(max_length=10, verbose_name=b'Source', choices=[(b'bb', b'BitBucket'), (b'gh', b'Github')])),
                ('repo_name', models.CharField(max_length=50, verbose_name=b'Respository Name')),
                ('repo_slug_name', models.SlugField(verbose_name=b'Respository Slug')),
                ('repo_branch', models.CharField(max_length=50, verbose_name=b'Branch')),
                ('repo_hook', models.BooleanField(default=False)),
                ('secret_key', models.CharField(default=b'x4sypYzDPm2nrltvb1XelchJ4anVq6', unique=True, max_length=30, verbose_name=b'Secret Key')),
                ('status', models.BooleanField(default=True)),
                ('status_message', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('notification', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='ftp_deploy.Notification', null=True)),
            ],
            options={
                'db_table': 'ftp_deploy_service',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50)),
                ('active', models.BooleanField(default=False)),
                ('service', models.ForeignKey(to='ftp_deploy.Service')),
            ],
            options={
                'db_table': 'ftp_deploy_task',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='log',
            name='service',
            field=models.ForeignKey(to='ftp_deploy.Service', blank=True),
            preserve_default=True,
        ),
    ]
