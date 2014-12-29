# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import easyui.mixins.model_mixins


def create_base_menu(apps, schema_editor):
    Menu = apps.get_model("easyui", "Menu")
    new_menu = Menu(1, '菜单权限', True, 0, '', '', '', False)
    new_menu.save()
    new_menu = Menu(2, '菜单列表', False, 1, 'easyui', 'MenuListView', '', False)
    new_menu.save()
    new_menu = Menu(3, '用户菜单权限', False, 1, 'easyui', 'UserMenuListView', '', False)
    new_menu.save()
    new_menu = Menu(4, '用户组菜单权限', False, 1, 'easyui', 'GroupMenuListView', '', False)
    new_menu.save()

class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupMenu',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('menus_show', models.TextField(help_text=b'JSON\xe6\xa0\xbc\xe5\xbc\x8f\xe7\x9a\x84\xe5\xad\x97\xe7\xac\xa6\xe4\xb8\xb2\xef\xbc\x8c\xe5\x9c\xa8\xe8\x8f\x9c\xe5\x8d\x95\xe6\x98\xbe\xe7\xa4\xba', verbose_name=b'\xe8\x8f\x9c\xe5\x8d\x95\xe6\x98\xbe\xe7\xa4\xba\xe6\x9d\x83\xe9\x99\x90', blank=True)),
                ('menus_checked', models.TextField(help_text=b'JSON\xe6\xa0\xbc\xe5\xbc\x8f\xe7\x9a\x84\xe5\xad\x97\xe7\xac\xa6\xe4\xb8\xb2, \xe4\xbf\x9d\xe7\x95\x99\xe7\x94\xa8\xe6\x88\xb7\xe7\xbb\x84checked\xe5\x86\x85\xe5\xae\xb9', verbose_name=b'\xe8\x8f\x9c\xe5\x8d\x95checked', blank=True)),
                ('group', models.ForeignKey(verbose_name=b'\xe7\x94\xa8\xe6\x88\xb7\xe7\xbb\x84', to='auth.Group', unique=True)),
            ],
            options={
                'verbose_name': '\u7528\u6237\u7ec4\u83dc\u5355\u6743\u9650',
                'verbose_name_plural': '\u7528\u6237\u7ec4\u83dc\u5355\u6743\u9650',
            },
            bases=(easyui.mixins.model_mixins.ModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(help_text=b'\xe6\x9c\x80\xe5\xa4\x9a100\xe4\xb8\xaa\xe8\x8b\xb1\xe6\x96\x87\xe5\xad\x97\xe6\xaf\x8d\xe9\x95\xbf', max_length=100, verbose_name=b'\xe8\x8f\x9c\xe5\x8d\x95\xe5\x90\x8d')),
                ('is_root', models.BooleanField(default=False, help_text=b'\xe8\xbf\x99\xe4\xb8\xaa\xe4\xb8\x8d\xe6\xb7\xbb\xe7\x9a\x84\xef\xbc\x8cform\xe4\xb8\xad\xe7\xbc\xba\xe7\x9c\x81\xe5\xa4\x84\xe7\x90\x86', verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe4\xb8\xba\xe6\xa0\xb9\xe8\x8a\x82\xe7\x82\xb9')),
                ('parent_id', models.IntegerField(verbose_name=b'\xe7\x88\xb6ID')),
                ('namespace', models.CharField(max_length=100, verbose_name=b'APP\xe5\x90\x8d', blank=True)),
                ('viewname', models.CharField(max_length=100, verbose_name=b'view\xe5\x90\x8d', blank=True)),
                ('kwargs', models.CharField(max_length=100, verbose_name=b'\xe9\x99\x84\xe5\x8a\xa0\xe5\x8f\x82\xe6\x95\xb0', blank=True)),
                ('is_system', models.BooleanField(default=False, help_text=b'\xe7\xb3\xbb\xe7\xbb\x9f\xe8\x8f\x9c\xe5\x8d\x95\xe5\x8f\xaa\xe5\xaf\xb9\xe8\xb6\x85\xe7\xba\xa7\xe7\x94\xa8\xe6\x88\xb7\xe5\x92\x8c\xe5\x90\x8e\xe5\x8f\xb0\xe7\x94\xa8\xe6\x88\xb7\xe6\x98\xbe\xe7\xa4\xba', verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe4\xb8\xba\xe7\xb3\xbb\xe7\xbb\x9f\xe8\x8f\x9c\xe5\x8d\x95', editable=False)),
            ],
            options={
                'verbose_name': '\u83dc\u5355',
                'verbose_name_plural': '\u83dc\u5355',
            },
            bases=(easyui.mixins.model_mixins.ModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='UserMenu',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('menus_show', models.TextField(help_text=b'JSON\xe6\xa0\xbc\xe5\xbc\x8f\xe7\x9a\x84\xe5\xad\x97\xe7\xac\xa6\xe4\xb8\xb2\xef\xbc\x8c\xe5\x9c\xa8\xe8\x8f\x9c\xe5\x8d\x95\xe6\x98\xbe\xe7\xa4\xba', verbose_name=b'\xe8\x8f\x9c\xe5\x8d\x95\xe6\x98\xbe\xe7\xa4\xba\xe6\x9d\x83\xe9\x99\x90', blank=True)),
                ('menus_checked', models.TextField(help_text=b'JSON\xe6\xa0\xbc\xe5\xbc\x8f\xe7\x9a\x84\xe5\xad\x97\xe7\xac\xa6\xe4\xb8\xb2, checked\xe7\x94\xa8\xe6\x88\xb7\xe6\x9d\x83\xe9\x99\x90\xe9\x85\x8d\xe7\xbd\xae', verbose_name=b'\xe8\x8f\x9c\xe5\x8d\x95checked', blank=True)),
                ('user', models.ForeignKey(verbose_name=b'\xe7\x94\xa8\xe6\x88\xb7', to=settings.AUTH_USER_MODEL, unique=True)),
            ],
            options={
                'verbose_name': '\u7528\u6237\u83dc\u5355\u6743\u9650',
                'verbose_name_plural': '\u7528\u6237\u83dc\u5355\u6743\u9650',
            },
            bases=(easyui.mixins.model_mixins.ModelMixin, models.Model),
        ),
        migrations.RunPython(create_base_menu),
    ]

