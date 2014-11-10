# flake8: noqa
# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'QuotationItem.manufacturer'
        db.add_column(u'aps_purchasing_quotationitem', 'manufacturer',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='quotations', null=True, to=orm['aps_purchasing.Manufacturer']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'QuotationItem.manufacturer'
        db.delete_column(u'aps_purchasing_quotationitem', 'manufacturer_id')


    models = {
        u'aps_bom.ipn': {
            'Meta': {'object_name': 'IPN'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'price_group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ipns'", 'to': u"orm['aps_bom.PriceGroup']"}),
            'price_max': ('django.db.models.fields.DecimalField', [], {'max_digits': '11', 'decimal_places': '3'}),
            'shape': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ipns'", 'to': u"orm['aps_bom.Shape']"})
        },
        u'aps_bom.pricegroup': {
            'Meta': {'object_name': 'PriceGroup'},
            'add': ('django.db.models.fields.DecimalField', [], {'default': "'0.00000'", 'max_digits': '10', 'decimal_places': '5'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rate': ('django.db.models.fields.DecimalField', [], {'default': "'1.00000'", 'max_digits': '10', 'decimal_places': '5'})
        },
        u'aps_bom.shape': {
            'Meta': {'object_name': 'Shape'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'aps_purchasing.aml': {
            'Meta': {'object_name': 'AML'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipn': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['aps_bom.IPN']"}),
            'manufacturer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['aps_purchasing.Manufacturer']"})
        },
        u'aps_purchasing.currency': {
            'Meta': {'object_name': 'Currency'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso_code': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'sign': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        u'aps_purchasing.distributor': {
            'Meta': {'object_name': 'Distributor'},
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['aps_purchasing.Currency']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'min_order_value': ('django.db.models.fields.DecimalField', [], {'max_digits': '11', 'decimal_places': '5'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'payment_terms': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'distributors'", 'to': u"orm['aps_purchasing.PaymentTerm']"}),
            'questionnaire_form': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'supplier_form': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'aps_purchasing.dpn': {
            'Meta': {'object_name': 'DPN'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'distributor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'DPNs'", 'to': u"orm['aps_purchasing.Distributor']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipn': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'DPNs'", 'null': 'True', 'to': u"orm['aps_bom.IPN']"}),
            'mpn': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'DPNs'", 'to': u"orm['aps_purchasing.MPN']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'aps_purchasing.manufacturer': {
            'Meta': {'object_name': 'Manufacturer'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'aps_purchasing.mpn': {
            'Meta': {'object_name': 'MPN'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manufacturer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['aps_purchasing.Manufacturer']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'pku': ('django.db.models.fields.FloatField', [], {}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['aps_purchasing.PackagingUnit']"})
        },
        u'aps_purchasing.packagingunit': {
            'Meta': {'object_name': 'PackagingUnit'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'aps_purchasing.paymentterm': {
            'Meta': {'object_name': 'PaymentTerm'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'aps_purchasing.price': {
            'Meta': {'object_name': 'Price'},
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'prices'", 'to': u"orm['aps_purchasing.Currency']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'moq': ('django.db.models.fields.DecimalField', [], {'max_digits': '11', 'decimal_places': '5'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '11', 'decimal_places': '5'}),
            'quotation_item': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'prices'", 'to': u"orm['aps_purchasing.QuotationItem']"})
        },
        u'aps_purchasing.quotation': {
            'Meta': {'object_name': 'Quotation'},
            'distributor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'quotations'", 'to': u"orm['aps_purchasing.Distributor']"}),
            'expiry_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_completed': ('django.db.models.fields.BooleanField', [], {}),
            'issuance_date': ('django.db.models.fields.DateTimeField', [], {}),
            'ref_number': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'aps_purchasing.quotationitem': {
            'Meta': {'object_name': 'QuotationItem'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manufacturer': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'quotations'", 'null': 'True', 'to': u"orm['aps_purchasing.Manufacturer']"}),
            'max_lead_time': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'min_lead_time': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'mpn': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'quotation_items'", 'to': u"orm['aps_purchasing.MPN']"}),
            'quotation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'quotation_items'", 'to': u"orm['aps_purchasing.Quotation']"})
        }
    }

    complete_apps = ['aps_purchasing']
