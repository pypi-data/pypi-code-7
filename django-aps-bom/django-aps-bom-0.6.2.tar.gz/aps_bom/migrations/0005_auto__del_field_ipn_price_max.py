# flake8: noqa
# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'IPN.price_max'
        db.delete_column(u'aps_bom_ipn', 'price_max')


    def backwards(self, orm):
        # Adding field 'IPN.price_max'
        db.add_column(u'aps_bom_ipn', 'price_max',
                      self.gf('django.db.models.fields.DecimalField')(default='0.00', max_digits=11, decimal_places=3),
                      keep_default=False)


    models = {
        u'aps_bom.additionaltext': {
            'Meta': {'object_name': 'AdditionalText'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipn': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'additional_texts'", 'to': u"orm['aps_bom.IPN']"}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'aps_bom.bom': {
            'Meta': {'object_name': 'BOM'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipn': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'boms'", 'null': 'True', 'to': u"orm['aps_bom.IPN']"})
        },
        u'aps_bom.bomitem': {
            'Meta': {'object_name': 'BOMItem'},
            'bom': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bomitems'", 'to': u"orm['aps_bom.BOM']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipn': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bomitems'", 'to': u"orm['aps_bom.IPN']"}),
            'position': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'qty': ('django.db.models.fields.FloatField', [], {}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bomitems'", 'to': u"orm['aps_bom.Unit']"})
        },
        u'aps_bom.cbom': {
            'Meta': {'object_name': 'CBOM'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cboms'", 'to': u"orm['aps_bom.Company']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'html_link': ('django.db.models.fields.URLField', [], {'max_length': '256', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'version_date': ('django.db.models.fields.DateField', [], {})
        },
        u'aps_bom.cbomitem': {
            'Meta': {'object_name': 'CBOMItem'},
            'bom': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cbomitems'", 'to': u"orm['aps_bom.CBOM']"}),
            'consign': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'epn': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cbomitems'", 'to': u"orm['aps_bom.EPN']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'qty': ('django.db.models.fields.FloatField', [], {}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cbomitems'", 'to': u"orm['aps_bom.Unit']"})
        },
        u'aps_bom.company': {
            'Meta': {'object_name': 'Company'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'companies'", 'to': u"orm['aps_bom.Country']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'aps_bom.country': {
            'Meta': {'object_name': 'Country'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'aps_bom.epn': {
            'Meta': {'object_name': 'EPN'},
            'company': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'epns'", 'to': u"orm['aps_bom.Company']"}),
            'cpn': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'cpns'", 'null': 'True', 'to': u"orm['aps_bom.IPN']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'epn': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipn': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ipns'", 'null': 'True', 'to': u"orm['aps_bom.IPN']"})
        },
        u'aps_bom.ipn': {
            'Meta': {'object_name': 'IPN'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'price_group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ipns'", 'to': u"orm['aps_bom.PriceGroup']"}),
            'shape': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ipns'", 'to': u"orm['aps_bom.Shape']"})
        },
        u'aps_bom.pricegroup': {
            'Meta': {'object_name': 'PriceGroup'},
            'add': ('django.db.models.fields.DecimalField', [], {'default': "'0.00000'", 'max_digits': '10', 'decimal_places': '5'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rate': ('django.db.models.fields.DecimalField', [], {'default': "'1.00000'", 'max_digits': '10', 'decimal_places': '5'})
        },
        u'aps_bom.pricemarker': {
            'Meta': {'object_name': 'PriceMarker'},
            'date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipn': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'price_markers'", 'to': u"orm['aps_bom.IPN']"}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '5'})
        },
        u'aps_bom.shape': {
            'Meta': {'object_name': 'Shape'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'aps_bom.unit': {
            'Meta': {'object_name': 'Unit'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['aps_bom']
