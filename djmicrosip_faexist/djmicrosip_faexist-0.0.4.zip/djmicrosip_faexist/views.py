#encoding:utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
# user autentication
from .models import *
from .forms import PuntoVentaDocumentoForm
import csv
from django.http import HttpResponse
from django.views.generic.list import ListView
from django.db import router, connections
from datetime import datetime
from microsip_api.comun.sic_db import first_or_none

def GetPrecioVentaArticulo(articulo):
    precio_con_impuesto = 0
    precio_sin_impto_mn = 0 
    try:
        #Consulta el precio de lista (42)
        articuloprecio = ArticuloPrecio.objects.get(articulo__id=articulo.id,precio_empresa__id=42)
    except Exception, e:
        moneda = Moneda.objects.get(es_moneda_local= 'S')
        precio=0
        tipo_cambio = 1
    else:
        precio=articuloprecio.precio
        moneda = articuloprecio.moneda
        if not moneda.es_moneda_local == 'S':
            
            tipo_cambio = first_or_none(TipoCambio.objects.filter(moneda=moneda).order_by('-fecha'))
            if tipo_cambio:
                tipo_cambio = tipo_cambio.tipo_cambio
            else:
                tipo_cambio = 1                    
        else:
            tipo_cambio = 1
        precio_sin_impto_mn = precio * tipo_cambio
        
        using = router.db_for_write(Articulo)
        c = connections[using].cursor()
        query =  ''' EXECUTE PROCEDURE PRECIO_CON_IMPTO(%s, %s,'N',0,0, CURRENT_DATE,'P')'''
        c.execute(query,[articulo.id, precio_sin_impto_mn])
        precio_con_impuesto = c.fetchall()[0][0]
        c.close()

    return {
        'con_impuesto': precio_con_impuesto,
        'sin_impuesto': precio_sin_impto_mn
    } 

def GetSeriesArticulo(articulo):
    '''
    Obtiene los numero de serie con existencia de un articulo dado.
    '''
    series = []
    if articulo.seguimiento == 'S':
        series = ArticuloDiscretoExistencia.objects.filter(articulo_discreto__articulo=articulo, existencia__gt=0, articulo_discreto__tipo='S').values_list('articulo_discreto__clave', flat=True)
    return series

@login_required( login_url = '/login/' )
def index( request, template_name = 'djmicrosip_faexist/index.html' ):
    moneda = Moneda.objects.get(es_moneda_local= 'S')
    form = PuntoVentaDocumentoForm(request.POST or None)
    existencias_list = []
    errors = []
    messages = []

    if form.is_valid():
        cleaned_data = form.cleaned_data
        #Paramentros de factura
        linea = cleaned_data['linea']
        caja = cleaned_data['caja']
        cajero = cleaned_data['cajero']
        cliente = cleaned_data['cliente']
        cliente_clave = first_or_none(ClienteClave.objects.filter(cliente=cliente))
        cliente_direccion =  first_or_none( ClienteDireccion.objects.filter( cliente= cliente, es_ppal='N') )

        from microsip_api.comun.sic_db import get_existencias_articulo
        
        using = router.db_for_write(Articulo)

        # articulos almacenables de la linea indicada
        articulos_ids = Articulo.objects.filter(linea=linea, es_almacenable='S').values_list('id',flat=True)
        errors = []
        for id in articulos_ids:
            existencia = get_existencias_articulo(
                articulo_id = id, 
                connection_name = using, 
                fecha_inicio = datetime.now().strftime( "01/01/%Y" ),
                almacen = 'CONSOLIDADO', 
            )
            articulo = Articulo.objects.get(pk=id)
            precio = GetPrecioVentaArticulo(articulo=articulo)

            if existencia > 0:
                articulos_discretos = []
                if articulo.seguimiento == 'S':
                    articulos_discretos = ArticuloDiscretoExistencia.objects.filter(articulo_discreto__articulo=articulo, existencia__gt=0, articulo_discreto__tipo='S').values_list('articulo_discreto', flat = True)
                    if existencia == len(articulos_discretos):
                        existencias_list.append((id,existencia, precio, articulos_discretos))
                    else:
                        errors.append('series incorrectas', articulo.nombre)
                else:
                    existencias_list.append((id,existencia,precio,)) 

        if not errors and existencias_list:
            documento = PuntoVentaDocumento(
                id = -1,
                caja = caja,
                cajero = cajero,
                cliente= cliente,
                clave_cliente= cliente_clave,
                almacen = caja.almacen,
                moneda= moneda,
                tipo= 'V',
                tipo_cambio = 1,
                aplicado = 'N',
                fecha= datetime.now(),
                hora= datetime.now().strftime('%H:%M:%S'),
                importe_neto = 0,
                total_impuestos = 0,
                importe_donativo = 0,
                total_fpgc = 0,
                sistema_origen='PV',
                descripcion = 'VENTA DE LINEA %s'%linea.nombre,
                usuario_creador= request.user.username,
                tipo_gen_fac=None,
            )
            documento.save()
            messages.append('Venta Generada Correctamente')
            importe_total = 0
            for articulo_list in existencias_list:
                articulo_id = articulo_list[0]
                articulo_existencia = articulo_list[1]
                articulo_precio =  articulo_list[2]

                articulo = Articulo.objects.get(pk=articulo_id)
                
                
                precio_total_neto = articulo_precio['con_impuesto'] * articulo_existencia

                articulo_clave =  first_or_none(ArticuloClave.objects.filter(rol__es_ppal='S', articulo= articulo))

                detalle = PuntoVentaDocumentoDetalle.objects.create(
                    id =-1,
                    documento_pv = documento,    
                    clave_articulo = articulo_clave,       
                    articulo = articulo, 
                    unidades = articulo_existencia,                
                    unidades_dev =0,            
                    precio_unitario  = articulo_precio['sin_impuesto'],      
                    precio_unitario_impto = articulo_precio['con_impuesto'],   
                    fpgc_unitario  =0,         
                    porcentaje_descuento =0,
                    precio_total_neto = precio_total_neto,     
                    porcentaje_comis =0,       
                    rol = 'N',                     
                    posicion = -1,
                )

                # Si es un articulo de series se genera un articulo discreto punto de venta por cada serie
                if articulo.seguimiento == 'S':
                    articulos_discretos = articulo_list[3]
                    for articulo_discreto_id in articulos_discretos:
                        articulo_discreto = ArticuloDiscreto.objects.get(pk=articulo_discreto_id)
                        PuntoVentaArticuloDiscreto.objects.create(
                            id = -1,
                            detalle = detalle,
                            articulo_discreto = articulo_discreto,
                        )

                importe_total += precio_total_neto

            PuntoVentaCobro.objects.create(
                id=-1,
                tipo='C',
                documento_pv= documento,
                forma_cobro=caja.predeterminado_forma_cobro,
                importe=importe_total,
                tipo_cambio=1,
                importe_mon_doc=importe_total,
            )
            documento.importe_neto = importe_total
            documento.aplicado = 'S'
            documento.save(update_fields=['importe_neto', 'aplicado'])

        if not existencias_list and request.POST:
            errors.append(('No hay articulos por vender de la linea indicada',''))


    c = {
        'form':form,
        'errors' : errors,
        'messages': messages,
    }

    return render_to_response( template_name, c, context_instance = RequestContext( request ) )

    

