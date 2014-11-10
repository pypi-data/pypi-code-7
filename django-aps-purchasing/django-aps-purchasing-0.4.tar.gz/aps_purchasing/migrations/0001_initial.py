# flake8: noqa
# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AML'
        db.create_table(u'aps_purchasing_aml', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ipn', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['aps_bom.IPN'])),
            ('manufacturer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['aps_purchasing.Manufacturer'])),
        ))
        db.send_create_signal(u'aps_purchasing', ['AML'])

        # Adding model 'Currency'
        db.create_table(u'aps_purchasing_currency', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('iso_code', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('sign', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal(u'aps_purchasing', ['Currency'])

        # Adding model 'Distributor'
        db.create_table(u'aps_purchasing_distributor', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('questionnaire_form', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('supplier_form', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('min_order_value', self.gf('django.db.models.fields.DecimalField')(max_digits=11, decimal_places=5)),
            ('currency', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['aps_purchasing.Currency'])),
            ('payment_terms', self.gf('django.db.models.fields.related.ForeignKey')(related_name='distributors', to=orm['aps_purchasing.PaymentTerm'])),
            ('is_approved', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'aps_purchasing', ['Distributor'])

        # Adding model 'DPN'
        db.create_table(u'aps_purchasing_dpn', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('ipn', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='DPNs', null=True, to=orm['aps_bom.IPN'])),
            ('distributor', self.gf('django.db.models.fields.related.ForeignKey')(related_name='DPNs', to=orm['aps_purchasing.Distributor'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('mpn', self.gf('django.db.models.fields.related.ForeignKey')(related_name='DPNs', to=orm['aps_purchasing.MPN'])),
        ))
        db.send_create_signal(u'aps_purchasing', ['DPN'])

        # Adding model 'Manufacturer'
        db.create_table(u'aps_purchasing_manufacturer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'aps_purchasing', ['Manufacturer'])

        # Adding model 'MPN'
        db.create_table(u'aps_purchasing_mpn', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('manufacturer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['aps_purchasing.Manufacturer'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('pku', self.gf('django.db.models.fields.FloatField')()),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['aps_purchasing.PackagingUnit'])),
        ))
        db.send_create_signal(u'aps_purchasing', ['MPN'])

        # Adding model 'PackagingUnit'
        db.create_table(u'aps_purchasing_packagingunit', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'aps_purchasing', ['PackagingUnit'])

        # Adding model 'PaymentTerm'
        db.create_table(u'aps_purchasing_paymentterm', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'aps_purchasing', ['PaymentTerm'])

        # Adding model 'Price'
        db.create_table(u'aps_purchasing_price', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('quotation_item', self.gf('django.db.models.fields.related.ForeignKey')(related_name='prices', to=orm['aps_purchasing.QuotationItem'])),
            ('moq', self.gf('django.db.models.fields.DecimalField')(max_digits=11, decimal_places=5)),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=11, decimal_places=5)),
            ('currency', self.gf('django.db.models.fields.related.ForeignKey')(related_name='prices', to=orm['aps_purchasing.Currency'])),
        ))
        db.send_create_signal(u'aps_purchasing', ['Price'])

        # Adding model 'Quotation'
        db.create_table(u'aps_purchasing_quotation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('distributor', self.gf('django.db.models.fields.related.ForeignKey')(related_name='quotations', to=orm['aps_purchasing.Distributor'])),
            ('ref_number', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('issuance_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('expiry_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('is_completed', self.gf('django.db.models.fields.BooleanField')()),
        ))
        db.send_create_signal(u'aps_purchasing', ['Quotation'])

        # Adding model 'QuotationItem'
        db.create_table(u'aps_purchasing_quotationitem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('quotation', self.gf('django.db.models.fields.related.ForeignKey')(related_name='quotation_items', to=orm['aps_purchasing.Quotation'])),
            ('mpn', self.gf('django.db.models.fields.related.ForeignKey')(related_name='quotation_items', to=orm['aps_purchasing.MPN'])),
            ('min_lead_time', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('max_lead_time', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'aps_purchasing', ['QuotationItem'])


    def backwards(self, orm):
        # Deleting model 'AML'
        db.delete_table(u'aps_purchasing_aml')

        # Deleting model 'Currency'
        db.delete_table(u'aps_purchasing_currency')

        # Deleting model 'Distributor'
        db.delete_table(u'aps_purchasing_distributor')

        # Deleting model 'DPN'
        db.delete_table(u'aps_purchasing_dpn')

        # Deleting model 'Manufacturer'
        db.delete_table(u'aps_purchasing_manufacturer')

        # Deleting model 'MPN'
        db.delete_table(u'aps_purchasing_mpn')

        # Deleting model 'PackagingUnit'
        db.delete_table(u'aps_purchasing_packagingunit')

        # Deleting model 'PaymentTerm'
        db.delete_table(u'aps_purchasing_paymentterm')

        # Deleting model 'Price'
        db.delete_table(u'aps_purchasing_price')

        # Deleting model 'Quotation'
        db.delete_table(u'aps_purchasing_quotation')

        # Deleting model 'QuotationItem'
        db.delete_table(u'aps_purchasing_quotationitem')


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
            'max_lead_time': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'min_lead_time': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'mpn': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'quotation_items'", 'to': u"orm['aps_purchasing.MPN']"}),
            'quotation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'quotation_items'", 'to': u"orm['aps_purchasing.Quotation']"})
        }
    }

    complete_apps = ['aps_purchasing']
