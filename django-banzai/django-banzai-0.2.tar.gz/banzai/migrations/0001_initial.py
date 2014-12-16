# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Package'
        db.create_table('banzai_package', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=4, blank=True)),
            ('pack_id', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('emails_all', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('emails_correct', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('banzai', ['Package'])

        # Adding model 'Report'
        db.create_table('banzai_report', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('package', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['banzai.Package'])),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=4, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('reject_code', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('reject_message', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('banzai', ['Report'])

        # Adding model 'ReportFBL'
        db.create_table('banzai_reportfbl', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('package', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['banzai.Package'])),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=4, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
        ))
        db.send_create_signal('banzai', ['ReportFBL'])


    def backwards(self, orm):
        # Deleting model 'Package'
        db.delete_table('banzai_package')

        # Deleting model 'Report'
        db.delete_table('banzai_report')

        # Deleting model 'ReportFBL'
        db.delete_table('banzai_reportfbl')


    models = {
        'banzai.package': {
            'Meta': {'object_name': 'Package'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'emails_all': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'emails_correct': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pack_id': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '4', 'blank': 'True'})
        },
        'banzai.report': {
            'Meta': {'object_name': 'Report'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['banzai.Package']"}),
            'reject_code': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'reject_message': ('django.db.models.fields.TextField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '4', 'blank': 'True'})
        },
        'banzai.reportfbl': {
            'Meta': {'object_name': 'ReportFBL'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['banzai.Package']"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '4', 'blank': 'True'})
        }
    }

    complete_apps = ['banzai']