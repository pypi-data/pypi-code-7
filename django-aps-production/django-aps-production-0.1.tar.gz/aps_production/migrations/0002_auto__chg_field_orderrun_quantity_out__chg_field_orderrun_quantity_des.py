# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'OrderRun.quantity_out'
        db.alter_column(u'aps_production_orderrun', 'quantity_out', self.gf('django.db.models.fields.PositiveIntegerField')(null=True))

        # Changing field 'OrderRun.quantity_dest_out'
        db.alter_column(u'aps_production_orderrun', 'quantity_dest_out', self.gf('django.db.models.fields.PositiveIntegerField')(null=True))

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'OrderRun.quantity_out'
        raise RuntimeError("Cannot reverse this migration. 'OrderRun.quantity_out' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'OrderRun.quantity_out'
        db.alter_column(u'aps_production_orderrun', 'quantity_out', self.gf('django.db.models.fields.PositiveIntegerField')())

        # User chose to not deal with backwards NULL issues for 'OrderRun.quantity_dest_out'
        raise RuntimeError("Cannot reverse this migration. 'OrderRun.quantity_dest_out' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'OrderRun.quantity_dest_out'
        db.alter_column(u'aps_production_orderrun', 'quantity_dest_out', self.gf('django.db.models.fields.PositiveIntegerField')())

    models = {
        u'aps_bom.company': {
            'Meta': {'object_name': 'Company'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'companies'", 'to': u"orm['aps_bom.Country']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shipping_days': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'aps_bom.country': {
            'Meta': {'object_name': 'Country'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'aps_bom.ipn': {
            'Meta': {'ordering': "('code',)", 'object_name': 'IPN'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'code2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'price_group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ipns'", 'to': u"orm['aps_bom.PriceGroup']"}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ipns'", 'null': 'True', 'to': u"orm['aps_bom.Product']"}),
            'shape': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ipns'", 'to': u"orm['aps_bom.Shape']"}),
            'technology': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ipns'", 'null': 'True', 'to': u"orm['aps_bom.Technology']"})
        },
        u'aps_bom.pricegroup': {
            'Meta': {'object_name': 'PriceGroup'},
            'add': ('django.db.models.fields.DecimalField', [], {'default': "'0.00000'", 'max_digits': '10', 'decimal_places': '5'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rate': ('django.db.models.fields.DecimalField', [], {'default': "'1.00000'", 'max_digits': '10', 'decimal_places': '5'})
        },
        u'aps_bom.product': {
            'Meta': {'ordering': "('product_number',)", 'object_name': 'Product'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product_number': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'})
        },
        u'aps_bom.shape': {
            'Meta': {'ordering': "('code',)", 'object_name': 'Shape'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'aps_bom.technology': {
            'Meta': {'ordering': "('identifier',)", 'object_name': 'Technology'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'})
        },
        u'aps_production.error': {
            'Meta': {'object_name': 'Error'},
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'error_bin': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'errors'", 'to': u"orm['aps_production.ErrorBin']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order_run': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'errors'", 'to': u"orm['aps_production.OrderRun']"}),
            'quantity': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'aps_production.errorbin': {
            'Meta': {'ordering': "('error_code',)", 'object_name': 'ErrorBin'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'error_code': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'technology': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'error_bins'", 'to': u"orm['aps_bom.Technology']"})
        },
        u'aps_production.order': {
            'Meta': {'ordering': "('order_number',)", 'object_name': 'Order'},
            'company': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'orders'", 'to': u"orm['aps_bom.Company']"}),
            'customer_po_date': ('django.db.models.fields.DateTimeField', [], {}),
            'customer_po_number': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order_number': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        u'aps_production.orderline': {
            'Meta': {'ordering': "('order', 'line_no')", 'unique_together': "(('order', 'line_no'),)", 'object_name': 'OrderLine'},
            'date_requested': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_no': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'order_lines'", 'to': u"orm['aps_production.Order']"}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'order_lines'", 'to': u"orm['aps_bom.Product']"}),
            'quantity_ordered': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'aps_production.orderrun': {
            'Meta': {'object_name': 'OrderRun'},
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipn': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'order_runs'", 'to': u"orm['aps_bom.IPN']"}),
            'is_open': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'order_line': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'order_runs'", 'to': u"orm['aps_production.OrderLine']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'order_runs'", 'null': 'True', 'to': u"orm['aps_production.OrderRun']"}),
            'quantity_dest_out': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'quantity_out': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'quantity_started': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'run_number': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'aps_production.shipment': {
            'Meta': {'object_name': 'Shipment'},
            'date_shipped': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order_run': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'shipments'", 'to': u"orm['aps_production.OrderRun']"}),
            'quantity': ('django.db.models.fields.PositiveIntegerField', [], {})
        }
    }

    complete_apps = ['aps_production']