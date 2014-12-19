import os
MICROSIP_MODULES = (
	'django_microsip_base.libs.models_base',
	'microsip_api.apps.config',
    'microsip_api.apps.administrador',
    'django_microsip_base.apps.main',
)

# EXTRA_MODULES = (
    # 'django_microsip_base.apps.plugins.django-microsip-ventas-remgencargos.django-microsip-ventas-remgencargos',
    #'django_microsip_base.apps.plugins.django-microsip-cancela-cfdi.django-microsip-cancela-cfdi',

    # 'django_microsip_base.apps.plugins.django-microsip-consolidador.django-microsip-consolidador',
    # 'django_microsip_base.apps.plugins.django-microsip-liquida.django-microsip-liquida',
    # 'django_microsip_base.apps.plugins.django_microsip_catalogoarticulos.django_microsip_catalogoarticulos',
    # 'django_microsip_base.apps.plugins.django_microsip_consultaprecio.django_microsip_consultaprecio',
    # 'django_microsip_base.apps.plugins.django_microsip_diot.django_microsip_diot',
    # 'django_microsip_base.apps.plugins.django_msp_cotizacion.django_msp_cotizacion',
    # 'django_microsip_base.apps.plugins.django_msp_organizador.django_msp_organizador',
     # 'django-microsip-consolidador',
    # 'django_microsip_base.apps.plugins.django_sms.django_sms',
    # 'django_microsip_base.apps.plugins.django_msp_importa_inventario.django_msp_importa_inventario',
    # 'django_microsip_base.apps.plugins.django_msp_polizas.django_msp_polizas',
    #  'django_microsip_base.apps.plugins.django-microsip-quickbooks.django-microsip-quickbooks',
    #  'django_microsip_base.apps.plugins.microsip_exporta_xml.django_microsip_exporta_xml',
     # 'django_microsip_base.apps.plugins.django_msp_facturaglobal.django_msp_facturaglobal',
     # 'django_microsip_base.apps.plugins.django_microsip_puntos.django_microsip_puntos',
     # 'django_microsip_base.apps.plugins.django_sms.django_sms',
     # 'django_microsip_puntos',
     #'django_microsip_base.apps.plugins.django_microsip_catalogoprod.django_microsip_catalogoprod',
    # 'django_microsip_base.apps.plugins.django_msp_controldeacceso.django_msp_controldeacceso',
#     'django_microsip_base.apps.plugins.django_msp_inventarios.django_msp_inventarios',
#     'django_microsip_diot',
#     'django_msp_facturaglobal',

     

     
# # )
extra_list = os.environ['SIC_INSTALLED_APPS'].split(',')
extra_list.remove('')

EXTRA_MODULES = tuple(extra_list)

EXTRA_INFO = {
    'ruta_datos_facturacion': 'C:\sat',
}

MICROSIP_VERSION = os.environ['MICROSIP_VERSION']

import importlib, sys
EXTRA_APPS = []
for module in EXTRA_MODULES:
    try:
        module_config = importlib.import_module(module+'.config')
    except ImportError as exc:
        sys.stderr.write("Error: failed to import settings module ({})".format(exc))
    else:
        module_settings = module_config.settings

        EXTRA_APPS.append({
            'app': module,
            'name': module_settings['name'],
            'icon_class':module_settings['icon_class'],
            'url':module_settings['url'],
            'url_main_path':module_settings['url_main_path'],
            'users':module_settings['users'],
            }
        )
