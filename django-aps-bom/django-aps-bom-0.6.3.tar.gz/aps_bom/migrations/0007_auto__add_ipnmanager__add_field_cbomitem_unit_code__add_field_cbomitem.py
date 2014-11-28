# flake8: noqa
# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'IPNManager'
        db.create_table(u'aps_bom_ipnmanager', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'aps_bom', ['IPNManager'])

        # Adding field 'EPN.company_description'
        db.add_column(u'aps_bom_epn', 'company_description',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=256, blank=True),
                      keep_default=False)

        # Adding field 'EPN.ipn_code'
        db.add_column(u'aps_bom_epn', 'ipn_code',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=256, blank=True),
                      keep_default=False)

        # Adding field 'CBOMItem.unit_code'
        db.add_column(u'aps_bom_cbomitem', 'unit_code',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=5, blank=True),
                      keep_default=False)

        # Adding field 'CBOMItem.epn_code'
        db.add_column(u'aps_bom_cbomitem', 'epn_code',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=513, blank=True),
                      keep_default=False)

        # Adding field 'CBOMItem.bom_short_description'
        db.add_column(u'aps_bom_cbomitem', 'bom_short_description',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=128, blank=True),
                      keep_default=False)

        # save every item once so the new fields get updated
        for item in orm['aps_bom.cbomitem'].objects.all():
            item.save()
        for epn in orm['aps_bom.epn'].objects.all():
            epn.save()


    def backwards(self, orm):
        # Deleting model 'IPNManager'
        db.delete_table(u'aps_bom_ipnmanager')

        # Deleting field 'EPN.company_description'
        db.delete_column(u'aps_bom_epn', 'company_description')

        # Deleting field 'EPN.ipn_code'
        db.delete_column(u'aps_bom_epn', 'ipn_code')

        # Deleting field 'CBOMItem.unit_code'
        db.delete_column(u'aps_bom_cbomitem', 'unit_code')

        # Deleting field 'CBOMItem.epn_code'
        db.delete_column(u'aps_bom_cbomitem', 'epn_code')

        # Deleting field 'CBOMItem.bom_short_description'
        db.delete_column(u'aps_bom_cbomitem', 'bom_short_description')


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
            'bom_short_description': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'consign': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'epn': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cbomitems'", 'to': u"orm['aps_bom.EPN']"}),
            'epn_code': ('django.db.models.fields.CharField', [], {'max_length': '513', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'qty': ('django.db.models.fields.FloatField', [], {}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cbomitems'", 'to': u"orm['aps_bom.Unit']"}),
            'unit_code': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'})
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
            'company_description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'cpn': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'cpns'", 'null': 'True', 'to': u"orm['aps_bom.IPN']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'epn': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ipn': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ipns'", 'null': 'True', 'to': u"orm['aps_bom.IPN']"}),
            'ipn_code': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'})
        },
        u'aps_bom.ipn': {
            'Meta': {'object_name': 'IPN'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'code2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'price_group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ipns'", 'to': u"orm['aps_bom.PriceGroup']"}),
            'shape': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ipns'", 'to': u"orm['aps_bom.Shape']"})
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
