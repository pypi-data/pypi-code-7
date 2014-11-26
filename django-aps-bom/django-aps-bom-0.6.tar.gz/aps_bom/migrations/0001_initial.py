# flake8: noqa
# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AdditionalText'
        db.create_table(u'aps_bom_additionaltext', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ipn', self.gf('django.db.models.fields.related.ForeignKey')(related_name='additional_texts', to=orm['aps_bom.IPN'])),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'aps_bom', ['AdditionalText'])

        # Adding model 'BOM'
        db.create_table(u'aps_bom_bom', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('ipn', self.gf('django.db.models.fields.related.ForeignKey')(related_name='boms', to=orm['aps_bom.IPN'])),
        ))
        db.send_create_signal(u'aps_bom', ['BOM'])

        # Adding model 'BOMItem'
        db.create_table(u'aps_bom_bomitem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bom', self.gf('django.db.models.fields.related.ForeignKey')(related_name='bomitems', to=orm['aps_bom.BOM'])),
            ('ipn', self.gf('django.db.models.fields.related.ForeignKey')(related_name='bomitems', to=orm['aps_bom.IPN'])),
            ('position', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('qty', self.gf('django.db.models.fields.FloatField')()),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(related_name='bomitems', to=orm['aps_bom.Unit'])),
        ))
        db.send_create_signal(u'aps_bom', ['BOMItem'])

        # Adding model 'CBOM'
        db.create_table(u'aps_bom_cbom', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(related_name='cboms', to=orm['aps_bom.Company'])),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('html_link', self.gf('django.db.models.fields.URLField')(max_length=256)),
            ('product', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('version_date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal(u'aps_bom', ['CBOM'])

        # Adding model 'CBOMItem'
        db.create_table(u'aps_bom_cbomitem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bom', self.gf('django.db.models.fields.related.ForeignKey')(related_name='cbomitems', to=orm['aps_bom.CBOM'])),
            ('epn', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('position', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('qty', self.gf('django.db.models.fields.FloatField')()),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(related_name='cbomitems', to=orm['aps_bom.Unit'])),
        ))
        db.send_create_signal(u'aps_bom', ['CBOMItem'])

        # Adding model 'Company'
        db.create_table(u'aps_bom_company', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(related_name='companies', to=orm['aps_bom.Country'])),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'aps_bom', ['Company'])

        # Adding model 'Country'
        db.create_table(u'aps_bom_country', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'aps_bom', ['Country'])

        # Adding model 'EPN'
        db.create_table(u'aps_bom_epn', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company', self.gf('django.db.models.fields.related.ForeignKey')(related_name='epns', to=orm['aps_bom.Company'])),
            ('cpn', self.gf('django.db.models.fields.related.ForeignKey')(related_name='cpns', to=orm['aps_bom.IPN'])),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('epn', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('ipn', self.gf('django.db.models.fields.related.ForeignKey')(related_name='ipns', to=orm['aps_bom.IPN'])),
        ))
        db.send_create_signal(u'aps_bom', ['EPN'])

        # Adding model 'IPN'
        db.create_table(u'aps_bom_ipn', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('price_group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='ipns', to=orm['aps_bom.PriceGroup'])),
            ('shape', self.gf('django.db.models.fields.related.ForeignKey')(related_name='ipns', to=orm['aps_bom.Shape'])),
            ('price_max', self.gf('django.db.models.fields.DecimalField')(max_digits=11, decimal_places=3)),
        ))
        db.send_create_signal(u'aps_bom', ['IPN'])

        # Adding model 'PriceGroup'
        db.create_table(u'aps_bom_pricegroup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('add', self.gf('django.db.models.fields.DecimalField')(default='0.00000', max_digits=10, decimal_places=5)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('rate', self.gf('django.db.models.fields.DecimalField')(default='1.00000', max_digits=10, decimal_places=5)),
        ))
        db.send_create_signal(u'aps_bom', ['PriceGroup'])

        # Adding model 'PriceMarker'
        db.create_table(u'aps_bom_pricemarker', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ipn', self.gf('django.db.models.fields.related.ForeignKey')(related_name='price_markers', to=orm['aps_bom.IPN'])),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=5)),
            ('date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal(u'aps_bom', ['PriceMarker'])

        # Adding model 'Shape'
        db.create_table(u'aps_bom_shape', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'aps_bom', ['Shape'])

        # Adding model 'Unit'
        db.create_table(u'aps_bom_unit', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal(u'aps_bom', ['Unit'])


    def backwards(self, orm):
        # Deleting model 'AdditionalText'
        db.delete_table(u'aps_bom_additionaltext')

        # Deleting model 'BOM'
        db.delete_table(u'aps_bom_bom')

        # Deleting model 'BOMItem'
        db.delete_table(u'aps_bom_bomitem')

        # Deleting model 'CBOM'
        db.delete_table(u'aps_bom_cbom')

        # Deleting model 'CBOMItem'
        db.delete_table(u'aps_bom_cbomitem')

        # Deleting model 'Company'
        db.delete_table(u'aps_bom_company')

        # Deleting model 'Country'
        db.delete_table(u'aps_bom_country')

        # Deleting model 'EPN'
        db.delete_table(u'aps_bom_epn')

        # Deleting model 'IPN'
        db.delete_table(u'aps_bom_ipn')

        # Deleting model 'PriceGroup'
        db.delete_table(u'aps_bom_pricegroup')

        # Deleting model 'PriceMarker'
        db.delete_table(u'aps_bom_pricemarker')

        # Deleting model 'Shape'
        db.delete_table(u'aps_bom_shape')

        # Deleting model 'Unit'
        db.delete_table(u'aps_bom_unit')


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
            'ipn': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'boms'", 'to': u"orm['aps_bom.IPN']"})
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
            'html_link': ('django.db.models.fields.URLField', [], {'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'version_date': ('django.db.models.fields.DateField', [], {})
        },
        u'aps_bom.cbomitem': {
            'Meta': {'object_name': 'CBOMItem'},
            'bom': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cbomitems'", 'to': u"orm['aps_bom.CBOM']"}),
            'epn': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
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
            'cpn': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cpns'", 'to': u"orm['aps_bom.IPN']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'epn': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipn': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ipns'", 'to': u"orm['aps_bom.IPN']"})
        },
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
