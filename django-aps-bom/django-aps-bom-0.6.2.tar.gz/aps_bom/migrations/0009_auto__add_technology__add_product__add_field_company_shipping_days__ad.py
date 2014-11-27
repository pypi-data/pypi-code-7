# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Technology'
        db.create_table(u'aps_bom_technology', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('identifier', self.gf('django.db.models.fields.CharField')(unique=True, max_length=3)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'aps_bom', ['Technology'])

        # Adding model 'Product'
        db.create_table(u'aps_bom_product', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product_number', self.gf('django.db.models.fields.CharField')(unique=True, max_length=256)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'aps_bom', ['Product'])

        # Adding field 'Company.shipping_days'
        db.add_column(u'aps_bom_company', 'shipping_days',
                      self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'IPN.technology'
        db.add_column(u'aps_bom_ipn', 'technology',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='ipns', null=True, to=orm['aps_bom.Technology']),
                      keep_default=False)

        # Adding field 'IPN.product'
        db.add_column(u'aps_bom_ipn', 'product',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='ipns', null=True, to=orm['aps_bom.Product']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'Technology'
        db.delete_table(u'aps_bom_technology')

        # Deleting model 'Product'
        db.delete_table(u'aps_bom_product')

        # Deleting field 'Company.shipping_days'
        db.delete_column(u'aps_bom_company', 'shipping_days')

        # Deleting field 'IPN.technology'
        db.delete_column(u'aps_bom_ipn', 'technology_id')

        # Deleting field 'IPN.product'
        db.delete_column(u'aps_bom_ipn', 'product_id')


    models = {
        u'aps_bom.additionaltext': {
            'Meta': {'object_name': 'AdditionalText'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipn': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'additional_texts'", 'to': u"orm['aps_bom.IPN']"}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'aps_bom.bom': {
            'Meta': {'ordering': "('ipn__code',)", 'object_name': 'BOM'},
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
            'bom_short_description': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'consign': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'epn': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cbomitems'", 'to': u"orm['aps_bom.EPN']"}),
            'epn_code': ('django.db.models.fields.CharField', [], {'max_length': '513', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.CharField', [], {'max_length': '7'}),
            'qty': ('django.db.models.fields.FloatField', [], {}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cbomitems'", 'to': u"orm['aps_bom.Unit']"}),
            'unit_code': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'})
        },
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
        u'aps_bom.epn': {
            'Meta': {'ordering': "('epn',)", 'object_name': 'EPN'},
            'company': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'epns'", 'to': u"orm['aps_bom.Company']"}),
            'company_description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'cpn': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'cpns'", 'null': 'True', 'to': u"orm['aps_bom.IPN']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'epn': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipn': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ipns'", 'null': 'True', 'to': u"orm['aps_bom.IPN']"}),
            'ipn_code': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'})
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
        u'aps_bom.ipnmanager': {
            'Meta': {'object_name': 'IPNManager'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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
        u'aps_bom.unit': {
            'Meta': {'object_name': 'Unit'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['aps_bom']