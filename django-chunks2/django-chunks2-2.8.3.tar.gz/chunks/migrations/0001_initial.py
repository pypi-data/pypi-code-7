# -*- coding: utf-8 -*-

from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Chunk'
        db.create_table('chunks_chunk', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('content', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('chunks', ['Chunk'])

        # Adding model 'Image'
        db.create_table('chunks_image', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=255)),
        ))
        db.send_create_signal('chunks', ['Image'])

        # Adding model 'Media'
        db.create_table('chunks_media', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('desc', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
            ('media', self.gf('django.db.models.fields.files.FileField')(max_length=256, null=True, blank=True)),
        ))
        db.send_create_signal('chunks', ['Media'])

    def backwards(self, orm):
        # Deleting model 'Chunk'
        db.delete_table('chunks_chunk')

        # Deleting model 'Image'
        db.delete_table('chunks_image')

        # Deleting model 'Media'
        db.delete_table('chunks_media')

    models = {
        'chunks.chunk': {
            'Meta': {'ordering': "('key',)", 'object_name': 'Chunk'},
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'chunks.image': {
            'Meta': {'ordering': "('key',)", 'object_name': 'Image'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '255'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'chunks.media': {
            'Meta': {'ordering': "('key',)", 'object_name': 'Media'},
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'media': ('django.db.models.fields.files.FileField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
        }
    }

    complete_apps = ['chunks']
