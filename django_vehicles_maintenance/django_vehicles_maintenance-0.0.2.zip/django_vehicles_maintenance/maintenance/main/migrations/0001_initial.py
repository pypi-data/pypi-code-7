# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'chassis'
        db.create_table('main_chassis', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('brand', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('line', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('color', self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True)),
            ('model', self.gf('django.db.models.fields.CharField')(max_length=4, null=True, blank=True)),
            ('license_plates', self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True)),
            ('mileage', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(default='N', max_length=10)),
        ))
        db.send_create_signal('main', ['chassis'])

        # Adding model 'storage_tank'
        db.create_table('main_storage_tank', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('series', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('brand', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('model', self.gf('django.db.models.fields.CharField')(max_length=4, null=True, blank=True)),
            ('water_nominal_cap', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('capArt', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('content', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(default='N', max_length=10)),
        ))
        db.send_create_signal('main', ['storage_tank'])

        # Adding model 'carburetion_tank'
        db.create_table('main_carburetion_tank', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('series', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('brand', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('model', self.gf('django.db.models.fields.CharField')(max_length=4, null=True, blank=True)),
            ('capacity', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(default='N', max_length=10)),
        ))
        db.send_create_signal('main', ['carburetion_tank'])

        # Adding model 'radio'
        db.create_table('main_radio', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('series', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('brand', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('model', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(default='N', max_length=10)),
        ))
        db.send_create_signal('main', ['radio'])

        # Adding model 'vehicle'
        db.create_table('main_vehicle', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('chassis', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.chassis'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('storage_tank', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.storage_tank'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('carburetion_tank', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.carburetion_tank'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('radio', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.radio'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('vehicle_type', self.gf('django.db.models.fields.CharField')(default='TR', max_length=10)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('main', ['vehicle'])

        # Adding model 'garage'
        db.create_table('main_garage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('office_phone', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
        ))
        db.send_create_signal('main', ['garage'])

        # Adding model 'radio_maintenance'
        db.create_table('main_radio_maintenance', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('garage', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.garage'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('radio', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.radio'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('main', ['radio_maintenance'])

        # Adding model 'chassis_maintenance'
        db.create_table('main_chassis_maintenance', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('garage', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.garage'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('chassis', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.chassis'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('mileage', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
        ))
        db.send_create_signal('main', ['chassis_maintenance'])

        # Adding model 'storage_tank_maintenance'
        db.create_table('main_storage_tank_maintenance', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('garage', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.garage'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('storage_tank', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.storage_tank'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
        ))
        db.send_create_signal('main', ['storage_tank_maintenance'])

        # Adding model 'carburetion_tank_maintenance'
        db.create_table('main_carburetion_tank_maintenance', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('garage', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.garage'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('carburetion_tank', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.carburetion_tank'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
        ))
        db.send_create_signal('main', ['carburetion_tank_maintenance'])

        # Adding model 'service'
        db.create_table('main_service', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('service_type', self.gf('django.db.models.fields.CharField')(default='CH', max_length=10)),
        ))
        db.send_create_signal('main', ['service'])

        # Adding model 'services_group'
        db.create_table('main_services_group', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60)),
        ))
        db.send_create_signal('main', ['services_group'])

        # Adding model 'services_group_items'
        db.create_table('main_services_group_items', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('services', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.service'])),
            ('services_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.services_group'])),
        ))
        db.send_create_signal('main', ['services_group_items'])

        # Adding model 'chassis_maintenance_S'
        db.create_table('main_chassis_maintenance_s', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('chassis_maintenance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.chassis_maintenance'])),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.service'], null=True, on_delete=models.SET_NULL, blank=True)),
        ))
        db.send_create_signal('main', ['chassis_maintenance_S'])

        # Adding model 'chassis_maintenance_Service'
        db.create_table('main_chassis_maintenance_service', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('chassis_maintenance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.chassis_maintenance'])),
            ('service', self.gf('django.db.models.fields.CharField')(max_length=150)),
        ))
        db.send_create_signal('main', ['chassis_maintenance_Service'])

        # Adding model 'chassis_maintenance_SG'
        db.create_table('main_chassis_maintenance_sg', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('chassis_maintenance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.chassis_maintenance'])),
            ('services_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.services_group'], null=True, on_delete=models.SET_NULL, blank=True)),
        ))
        db.send_create_signal('main', ['chassis_maintenance_SG'])

        # Adding model 'radio_maintenance_S'
        db.create_table('main_radio_maintenance_s', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('radio_maintenance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.radio_maintenance'])),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.service'], null=True, on_delete=models.SET_NULL, blank=True)),
        ))
        db.send_create_signal('main', ['radio_maintenance_S'])

        # Adding model 'radio_maintenance_SG'
        db.create_table('main_radio_maintenance_sg', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('radio_maintenance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.radio_maintenance'])),
            ('services_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.services_group'], null=True, on_delete=models.SET_NULL, blank=True)),
        ))
        db.send_create_signal('main', ['radio_maintenance_SG'])

        # Adding model 'storage_tank_maintenance_S'
        db.create_table('main_storage_tank_maintenance_s', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('storage_tank_maintenance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.storage_tank_maintenance'])),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.service'], null=True, on_delete=models.SET_NULL, blank=True)),
        ))
        db.send_create_signal('main', ['storage_tank_maintenance_S'])

        # Adding model 'storage_tank_maintenance_SG'
        db.create_table('main_storage_tank_maintenance_sg', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('storage_tank_maintenance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.storage_tank_maintenance'])),
            ('services_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.services_group'], null=True, on_delete=models.SET_NULL, blank=True)),
        ))
        db.send_create_signal('main', ['storage_tank_maintenance_SG'])

        # Adding model 'carburetion_tank_S'
        db.create_table('main_carburetion_tank_s', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('carburetion_tank_maintenance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.carburetion_tank_maintenance'])),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.service'], null=True, on_delete=models.SET_NULL, blank=True)),
        ))
        db.send_create_signal('main', ['carburetion_tank_S'])

        # Adding model 'carburetion_tank_SG'
        db.create_table('main_carburetion_tank_sg', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('carburetion_tank_maintenance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.carburetion_tank_maintenance'])),
            ('services_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.services_group'], null=True, on_delete=models.SET_NULL, blank=True)),
        ))
        db.send_create_signal('main', ['carburetion_tank_SG'])


    def backwards(self, orm):
        # Deleting model 'chassis'
        db.delete_table('main_chassis')

        # Deleting model 'storage_tank'
        db.delete_table('main_storage_tank')

        # Deleting model 'carburetion_tank'
        db.delete_table('main_carburetion_tank')

        # Deleting model 'radio'
        db.delete_table('main_radio')

        # Deleting model 'vehicle'
        db.delete_table('main_vehicle')

        # Deleting model 'garage'
        db.delete_table('main_garage')

        # Deleting model 'radio_maintenance'
        db.delete_table('main_radio_maintenance')

        # Deleting model 'chassis_maintenance'
        db.delete_table('main_chassis_maintenance')

        # Deleting model 'storage_tank_maintenance'
        db.delete_table('main_storage_tank_maintenance')

        # Deleting model 'carburetion_tank_maintenance'
        db.delete_table('main_carburetion_tank_maintenance')

        # Deleting model 'service'
        db.delete_table('main_service')

        # Deleting model 'services_group'
        db.delete_table('main_services_group')

        # Deleting model 'services_group_items'
        db.delete_table('main_services_group_items')

        # Deleting model 'chassis_maintenance_S'
        db.delete_table('main_chassis_maintenance_s')

        # Deleting model 'chassis_maintenance_Service'
        db.delete_table('main_chassis_maintenance_service')

        # Deleting model 'chassis_maintenance_SG'
        db.delete_table('main_chassis_maintenance_sg')

        # Deleting model 'radio_maintenance_S'
        db.delete_table('main_radio_maintenance_s')

        # Deleting model 'radio_maintenance_SG'
        db.delete_table('main_radio_maintenance_sg')

        # Deleting model 'storage_tank_maintenance_S'
        db.delete_table('main_storage_tank_maintenance_s')

        # Deleting model 'storage_tank_maintenance_SG'
        db.delete_table('main_storage_tank_maintenance_sg')

        # Deleting model 'carburetion_tank_S'
        db.delete_table('main_carburetion_tank_s')

        # Deleting model 'carburetion_tank_SG'
        db.delete_table('main_carburetion_tank_sg')


    models = {
        'main.carburetion_tank': {
            'Meta': {'object_name': 'carburetion_tank'},
            'brand': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'capacity': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'series': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '10'})
        },
        'main.carburetion_tank_maintenance': {
            'Meta': {'object_name': 'carburetion_tank_maintenance'},
            'carburetion_tank': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.carburetion_tank']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'garage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.garage']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'main.carburetion_tank_s': {
            'Meta': {'object_name': 'carburetion_tank_S'},
            'carburetion_tank_maintenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.carburetion_tank_maintenance']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.service']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        'main.carburetion_tank_sg': {
            'Meta': {'object_name': 'carburetion_tank_SG'},
            'carburetion_tank_maintenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.carburetion_tank_maintenance']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'services_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.services_group']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        'main.chassis': {
            'Meta': {'object_name': 'chassis'},
            'brand': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'color': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'license_plates': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'line': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'mileage': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '10'})
        },
        'main.chassis_maintenance': {
            'Meta': {'object_name': 'chassis_maintenance'},
            'chassis': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.chassis']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'garage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.garage']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mileage': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        },
        'main.chassis_maintenance_s': {
            'Meta': {'object_name': 'chassis_maintenance_S'},
            'chassis_maintenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.chassis_maintenance']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.service']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        'main.chassis_maintenance_service': {
            'Meta': {'object_name': 'chassis_maintenance_Service'},
            'chassis_maintenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.chassis_maintenance']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'service': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        'main.chassis_maintenance_sg': {
            'Meta': {'object_name': 'chassis_maintenance_SG'},
            'chassis_maintenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.chassis_maintenance']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'services_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.services_group']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        'main.garage': {
            'Meta': {'object_name': 'garage'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'office_phone': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'})
        },
        'main.radio': {
            'Meta': {'object_name': 'radio'},
            'brand': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'series': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '10'})
        },
        'main.radio_maintenance': {
            'Meta': {'object_name': 'radio_maintenance'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'garage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.garage']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'radio': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.radio']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        'main.radio_maintenance_s': {
            'Meta': {'object_name': 'radio_maintenance_S'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'radio_maintenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.radio_maintenance']"}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.service']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        'main.radio_maintenance_sg': {
            'Meta': {'object_name': 'radio_maintenance_SG'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'radio_maintenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.radio_maintenance']"}),
            'services_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.services_group']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        'main.service': {
            'Meta': {'object_name': 'service'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'service_type': ('django.db.models.fields.CharField', [], {'default': "'CH'", 'max_length': '10'})
        },
        'main.services_group': {
            'Meta': {'object_name': 'services_group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        },
        'main.services_group_items': {
            'Meta': {'object_name': 'services_group_items'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'services': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.service']"}),
            'services_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.services_group']"})
        },
        'main.storage_tank': {
            'Meta': {'object_name': 'storage_tank'},
            'brand': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'capArt': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'content': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'series': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '10'}),
            'water_nominal_cap': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        },
        'main.storage_tank_maintenance': {
            'Meta': {'object_name': 'storage_tank_maintenance'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'garage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.garage']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'storage_tank': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.storage_tank']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        'main.storage_tank_maintenance_s': {
            'Meta': {'object_name': 'storage_tank_maintenance_S'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.service']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'storage_tank_maintenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.storage_tank_maintenance']"})
        },
        'main.storage_tank_maintenance_sg': {
            'Meta': {'object_name': 'storage_tank_maintenance_SG'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'services_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.services_group']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'storage_tank_maintenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.storage_tank_maintenance']"})
        },
        'main.vehicle': {
            'Meta': {'object_name': 'vehicle'},
            'carburetion_tank': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.carburetion_tank']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'chassis': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.chassis']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'radio': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.radio']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'storage_tank': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.storage_tank']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'vehicle_type': ('django.db.models.fields.CharField', [], {'default': "'TR'", 'max_length': '10'})
        }
    }

    complete_apps = ['main']