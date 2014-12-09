# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('br_addresses', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='address',
            options={'ordering': ['created'], 'verbose_name': 'Endere\xe7o', 'verbose_name_plural': 'Endere\xe7os'},
        ),
        migrations.AlterModelOptions(
            name='city',
            options={'ordering': ('state', 'name'), 'verbose_name': 'Cidade', 'verbose_name_plural': 'Cidades'},
        ),
        migrations.AlterField(
            model_name='address',
            name='city',
            field=models.ForeignKey(verbose_name='Cidade', to='br_addresses.City'),
        ),
        migrations.AlterField(
            model_name='address',
            name='complement',
            field=models.TextField(null=True, verbose_name='Complemento', blank=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='kind_street',
            field=models.CharField(max_length=2, verbose_name='Tipo logradouro', choices=[(b'1', 'Aeroporto'), (b'2', 'Alameda'), (b'3', '\xc1rea'), (b'4', 'Avenida'), (b'5', 'Campo'), (b'6', 'Chac\xe1ra'), (b'7', 'Col\xf4nia'), (b'8', 'Condom\xednio'), (b'9', 'Conjunto'), (b'10', 'Distrito'), (b'11', 'Esplanada'), (b'12', 'Esta\xe7\xe3o'), (b'13', 'Estrada'), (b'14', 'Favela'), (b'15', 'fazenda'), (b'16', 'Feira'), (b'17', 'Jardim'), (b'18', 'Ladeira'), (b'19', 'Lago'), (b'20', 'Lagoa'), (b'21', 'Largo'), (b'22', 'Loteamento'), (b'23', 'Morro'), (b'24', 'N\xfacleo'), (b'25', 'Parque'), (b'26', 'Passarela'), (b'27', 'P\xe1tio'), (b'28', 'Pra\xe7a'), (b'29', 'Quadra'), (b'30', 'Recanto'), (b'31', 'Resid\xeancial'), (b'32', 'Rodovia'), (b'33', 'Rua'), (b'34', 'Setor'), (b'35', 'S\xedtio'), (b'36', 'Travessa'), (b'37', 'Trecho'), (b'38', 'Trevo'), (b'39', 'Vale'), (b'40', 'Vereda'), (b'41', 'Estrada'), (b'42', 'Viaduto'), (b'43', 'Viela'), (b'44', 'Vila')]),
        ),
        migrations.AlterField(
            model_name='address',
            name='neighborhood',
            field=models.CharField(default='center', max_length=100, verbose_name='Bairro'),
        ),
        migrations.AlterField(
            model_name='address',
            name='number',
            field=models.IntegerField(default=1000, verbose_name='N\xfamero'),
        ),
        migrations.AlterField(
            model_name='address',
            name='street',
            field=models.CharField(help_text='Rua ou avenida ou viela ou rodovia ... mais um endere\xe7o', max_length=100, verbose_name='Rua'),
        ),
        migrations.AlterField(
            model_name='address',
            name='zip_code',
            field=models.CharField(max_length=9, verbose_name='Cep'),
        ),
        migrations.AlterField(
            model_name='city',
            name='state',
            field=models.CharField(max_length=2, verbose_name='Estado', choices=[('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amap\xe1'), ('AM', 'Amazonas'), ('BA', 'Bahia'), ('CE', 'Cear\xe1'), ('DF', 'Distrito Federal'), ('ES', 'Esp\xedrito Santo'), ('GO', 'Goi\xe1s'), ('MA', 'Maranh\xe3o'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'), ('PA', 'Par\xe1'), ('PB', 'Para\xedba'), ('PR', 'Paran\xe1'), ('PE', 'Pernambuco'), ('PI', 'Piau\xed'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'), ('RS', 'Rio Grande do Sul'), ('RO', 'Rond\xf4nia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'), ('SP', 'S\xe3o Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins')]),
        ),
    ]
