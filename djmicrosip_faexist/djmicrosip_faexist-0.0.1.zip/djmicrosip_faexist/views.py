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
from django.db import router
from datetime import datetime
from microsip_api.comun.sic_db import first_or_none

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
    form = PuntoVentaDocumentoForm(request.POST or None)
    existencias_list = []
    errors = []
    if form.is_valid():
        cleaned_data = form.cleaned_data
        #Paramentros de factura
        linea = cleaned_data['linea']
        caja = cleaned_data['caja']
        cajero = cleaned_data['cajero']
        cliente = cleaned_data['cliente']
        cliente_clave = first_or_none(ClienteClave.objects.filter(cliente=cliente))
        cliente_direccion =  first_or_none( ClienteDireccion.objects.filter( cliente= cliente, es_ppal='N') )
        moneda = Moneda.objects.get(pk= 1)

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
            try:
                #Consulta el precio de lista (42)
                articuloprecio = ArticuloPrecio.objects.get(articulo__id=id,precio_empresa__id=42)
            except Exception, e:
                precio=0
            else:
                precio=articuloprecio.precio

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
            importe_total = 0
            for articulo_list in existencias_list:
                articulo_id = articulo_list[0]
                articulo_exitencia = articulo_list[1]
                articulo_precio =  articulo_list[2]

                articulo = Articulo.objects.get(pk=articulo_id)
                
                
                precio_total_neto = articulo_precio * articulo_exitencia

                articulo_clave =  first_or_none(ArticuloClave.objects.filter(rol__es_ppal='S', articulo= articulo))

                detalle = PuntoVentaDocumentoDetalle.objects.create(
                    id =-1,
                    documento_pv = documento,    
                    clave_articulo = articulo_clave,       
                    articulo = articulo, 
                    unidades =articulo_exitencia,                
                    unidades_dev =0,            
                    precio_unitario  = articulo_precio,      
                    precio_unitario_impto = articulo_precio,   
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

            # c = connections[connection_name].cursor()
            # query =  '''INSERT INTO impuestos_doctos_pv (docto_pv_id, impuesto_id, venta_neta, otros_impuestos, pctje_impuesto, importe_impuesto) \
            #     VALUES (%s, %s, 0.01, 0, 0, 0)'''
            # c.execute(query,[documento.id,  int(impuesto_al_0.id),])
            # c.close()

    c = {
        'form':form,
        'errors' : errors,
    }

    return render_to_response( template_name, c, context_instance = RequestContext( request ) )

    

