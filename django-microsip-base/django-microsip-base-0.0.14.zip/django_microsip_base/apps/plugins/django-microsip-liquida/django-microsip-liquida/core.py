#encoding:utf-8
import os, dbf
from django.conf import settings
from datetime import datetime
from .models import Registry
from django.db import router

def get_facturasmes_liquidacion():
    ''' Funcion para traer facturas del mes actual de programa liquidacion.'''
    using = router.db_for_write(Registry)
    ruta_carpeta_liquida = Registry.objects.get(nombre='SIC_EnlaceLiquida_RutaLiquidacion').get_value()
    empresas_a_ignorar = Registry.objects.get(nombre='SIC_EnlaceLiquida_EmpresasAIgnorar').get_value()
    conexion_no = using.split('-')[0]
    if empresas_a_ignorar:
        empresas_a_ignorar = empresas_a_ignorar.split(',')
        empresas_a_ignorar = [ conexion_no + '-' + empresa for empresa in empresas_a_ignorar ]
    else:
        empresas_a_ignorar = []

    #Precios
    precios = dbf.Table(os.path.join(ruta_carpeta_liquida,"enlace_microsip_precios_mes.dbf")).open()
    quincena1_precio = precios[0].precio1
    quincena2_precio = precios[0].precio2

    #Detalles
    detalles_rows = dbf.Table(os.path.join(ruta_carpeta_liquida,"enlace_microsip_saldos.dbf")).open()
    detalles_count = len(detalles_rows)
    errors = []

    if len(detalles_rows) > 0:
        primer_detalle_fecha = detalles_rows[0].fecha
        if datetime.today().month != primer_detalle_fecha.month or datetime.today().year != primer_detalle_fecha.year:
            errors.append('no se encontraron liquidaciones del mes.')

    facturas = []
    detalles = []
    ultima_clave = 0
    importe_neto = 0
    if not errors:
        #Formateamos facturas
        for contador, detalle_row in enumerate(detalles_rows):
            if str(detalle_row.clave) not in empresas_a_ignorar:
                detalle =  [detalle_row.fecha, detalle_row.kilos1, quincena2_precio ,detalle_row.importe1]
                if datetime.today().month != detalle_row.fecha.month or datetime.today().year != detalle_row.fecha.year:
                    errors.append('fecha_invalida')
                if detalle_row.clave != ultima_clave or contador == detalles_count-1:
                    if detalles != []:
                        facturas.append({'empresa_clave':ultima_clave, 'detalles':detalles, 'importe_neto':importe_neto})
                        importe_neto=0

                    detalles= []
                    detalle =  [detalle_row.fecha, detalle_row.kilos1, quincena1_precio, detalle_row.importe1]
                    detalles.append(detalle)
                    importe_neto = importe_neto + detalle_row.importe1
                else:
                    detalles.append(detalle)
                    importe_neto = importe_neto + detalle_row.importe1

                ultima_clave = detalle_row.clave
    if errors:
        facturas = []
    
    return facturas, errors

from django_microsip_base.libs.models_base.models import Registry

def get_indices(bases_de_datos_count, incremento, tipo):
    ''' Obtiene los indices de las bases de datos a sincronizar.'''

    registro = Registry.objects.get( nombre = 'SIC_INDICE_BASES_DATOS_SYN' ).valor
    registro_split = registro.split(';')
    
    if len(registro_split) == 2:
        registro_tipo = registro_split[0]
        indice = int(registro_split[1])
        if registro_tipo != tipo:
            indice = 0
    else:
        indice = 0

    indice_final = indice + incremento
    if indice_final > bases_de_datos_count:
        indice_final = bases_de_datos_count

    return indice, indice_final

def set_indices(indice_final, bases_de_datos_count, tipo):
    ''' Guarda el indice  en el que continuara sincronizando con bases de datos.'''
    
    indice = indice_final
    if indice == bases_de_datos_count:
        indice = 0
    registro = Registry.objects.get( nombre = 'SIC_INDICE_BASES_DATOS_SYN' )
    registro.valor = "%s;%s"%(tipo, indice)
    registro.save()