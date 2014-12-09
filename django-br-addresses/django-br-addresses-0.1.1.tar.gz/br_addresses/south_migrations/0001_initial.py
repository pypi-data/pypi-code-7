# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'City'
        db.create_table(u'br_addresses_city', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'br_addresses', ['City'])

        # Adding unique constraint on 'City', fields ['name', 'state']
        db.create_unique(u'br_addresses_city', ['name', 'state'])

        # Adding model 'Address'
        db.create_table(u'br_addresses_address', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, blank=True)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(max_length=9)),
            ('neighborhood', self.gf('django.db.models.fields.CharField')(default=u'center', max_length=100)),
            ('kind_street', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('number', self.gf('django.db.models.fields.IntegerField')(default=1000)),
            ('complement', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length='200')),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['br_addresses.City'])),
        ))
        db.send_create_signal(u'br_addresses', ['Address'])


    def backwards(self, orm):
        # Removing unique constraint on 'City', fields ['name', 'state']
        db.delete_unique(u'br_addresses_city', ['name', 'state'])

        # Deleting model 'City'
        db.delete_table(u'br_addresses_city')

        # Deleting model 'Address'
        db.delete_table(u'br_addresses_address')


    models = {
        u'br_addresses.address': {
            'Meta': {'ordering': "['created']", 'object_name': 'Address'},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['br_addresses.City']"}),
            'complement': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind_street': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'neighborhood': ('django.db.models.fields.CharField', [], {'default': "u'center'", 'max_length': '100'}),
            'number': ('django.db.models.fields.IntegerField', [], {'default': '1000'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': "'200'"}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '9'})
        },
        u'br_addresses.city': {
            'Meta': {'ordering': "('state', 'name')", 'unique_together': "(('name', 'state'),)", 'object_name': 'City'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        }
    }

    complete_apps = ['br_addresses']