# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'NavTree.name'
        db.add_column('coop_cms_navtree', 'name', self.gf('django.db.models.fields.CharField')(default='default', unique=True, max_length=100, db_index=True), keep_default=False)

        # Adding M2M table for field types on 'NavTree'
        db.create_table('coop_cms_navtree_types', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('navtree', models.ForeignKey(orm['coop_cms.navtree'], null=False)),
            ('navtype', models.ForeignKey(orm['coop_cms.navtype'], null=False))
        ))
        db.create_unique('coop_cms_navtree_types', ['navtree_id', 'navtype_id'])


    def backwards(self, orm):
        
        # Deleting field 'NavTree.name'
        db.delete_column('coop_cms_navtree', 'name')

        # Removing M2M table for field types on 'NavTree'
        db.delete_table('coop_cms_navtree_types')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'coop_cms.articlesection': {
            'Meta': {'object_name': 'ArticleSection'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'coop_cms.document': {
            'Meta': {'object_name': 'Document'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_private': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'})
        },
        'coop_cms.image': {
            'Meta': {'object_name': 'Image'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'})
        },
        'coop_cms.link': {
            'Meta': {'object_name': 'Link'},
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'coop_cms.navnode': {
            'Meta': {'unique_together': "(('content_type', 'object_id'),)", 'object_name': 'NavNode'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_navigation': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'ordering': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'default': '0', 'to': "orm['coop_cms.NavNode']", 'null': 'True', 'blank': 'True'})
        },
        'coop_cms.navtree': {
            'Meta': {'object_name': 'NavTree'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'default'", 'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'types': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['coop_cms.NavType']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'coop_cms.navtype': {
            'Meta': {'object_name': 'NavType'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label_rule': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'search_field': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'})
        },
        'coop_cms.newsletter': {
            'Meta': {'object_name': 'Newsletter'},
            'content': ('html_field.db.models.fields.HTMLField', [], {'default': "'<br>'", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'items': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['coop_cms.NewsletterItem']", 'symmetrical': 'False', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'template': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'})
        },
        'coop_cms.newsletteritem': {
            'Meta': {'unique_together': "(('content_type', 'object_id'),)", 'object_name': 'NewsletterItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'coop_cms.newslettersending': {
            'Meta': {'object_name': 'NewsletterSending'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'newsletter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['coop_cms.Newsletter']"}),
            'scheduling_dt': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'sending_dt': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'})
        },
        'coop_cms.pieceofhtml': {
            'Meta': {'object_name': 'PieceOfHtml'},
            'content': ('html_field.db.models.fields.HTMLField', [], {'default': "''", 'blank': 'True'}),
            'div_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['coop_cms']
