# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import PeerReviewApp.custom_fields
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Manuscript',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default=b'submitted', max_length=20)),
                ('title', models.CharField(unique=True, max_length=200)),
                ('brief_title', models.CharField(unique=True, max_length=50)),
                ('abstract', models.CharField(max_length=200000)),
                ('keywords', PeerReviewApp.custom_fields.SeparatedValuesField(help_text=b'Keywords, separated by a comma', max_length=1000)),
                ('field', models.CharField(max_length=200)),
                ('target_journal', models.CharField(max_length=200)),
                ('is_final', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ManuscriptFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('upload', models.FileField(null=True, upload_to=b'uploads/%Y/%m/%d', blank=True)),
                ('manuscript', models.ForeignKey(related_query_name=b'file', related_name=b'files', to='PeerReviewApp.Manuscript')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReviewPeriod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_full', models.BooleanField(default=False)),
                ('start_date', models.DateField(default=datetime.datetime(2014, 11, 27, 5, 35, 21, 535404))),
                ('submission_deadline', models.DateField()),
                ('review_deadline', models.DateField()),
                ('group_meeting_time', models.DateField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SiteUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('email', models.EmailField(help_text=b'Emory Email Address', unique=True, max_length=200, verbose_name=b'email address', error_messages={b'unique': b'A user with that email already exists.'})),
                ('first_name', models.CharField(help_text=b'First Name', max_length=100)),
                ('last_name', models.CharField(help_text=b'Last Name', max_length=100)),
                ('department', models.CharField(help_text=b'Department', max_length=200)),
                ('lab', models.CharField(help_text=b'Name of Lab', max_length=200)),
                ('pi', models.CharField(help_text=b'Name of Primary Investigator', max_length=200)),
                ('school', models.CharField(default=b'Goizueta Business School', max_length=100, choices=[(b'Goizueta Business School', b'Goizueta Business School'), (b'Laney Graduate School', b'Laney Graduate School'), (b'School of Law', b'School of Law'), (b'School of Medicine', b'School of Medicine'), (b'Nell Hodgson Woodruff School of Nursing', b'Nell Hodgson Woodruff School of Nursing'), (b'Rollins School of Public Health', b'Rollins School of Public Health'), (b'Candler School of Theology', b'Candler School of Theology'), (b'College of Arts and Sciences', b'College of Arts and Sciences'), (b'Other', b'Other')])),
                ('review_count', models.CharField(default=0, help_text=b'Number of Manuscripts you have reviewed', max_length=2)),
                ('agreed_to_form', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='manuscript',
            name='authors',
            field=models.ManyToManyField(related_query_name=b'author', related_name=b'authors', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='manuscript',
            name='review_period',
            field=models.ForeignKey(related_query_name=b'manuscript', related_name=b'manuscripts', default=0, to='PeerReviewApp.ReviewPeriod'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='manuscript',
            name='reviewers',
            field=models.ManyToManyField(related_query_name=b'reviewer', related_name=b'reviewers', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
