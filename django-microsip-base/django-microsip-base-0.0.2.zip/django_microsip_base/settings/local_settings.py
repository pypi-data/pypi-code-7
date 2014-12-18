import os
MICROSIP_MODULES = (
	'django_microsip_base.libs.models_base',
	'microsip_api.apps.config',
    'microsip_api.apps.administrador',
    'django_microsip_base.apps.main',
)

# EXTRA_MODULES = (
#     # 'django_microsip_base.apps.plugins.django-microsip-consolidador.django-microsip-consolidador',
#     # 'django-microsip-consolidador',
#     # 'django_msp_facturaglobal',
#     'django_microsip_base.apps.plugins.django_microsip_catalogoarticulos.django_microsip_catalogoarticulos',
#     # 'django_microsip_base.apps.plugins.django_microsip_consultaprecio.django_microsip_consultaprecio',
#     # 'django_microsip_base.apps.plugins.django_microsip_diot.django_microsip_diot',
#     # 'django_microsip_base.apps.plugins.django_msp_controldeacceso.django_msp_controldeacceso',
#     # 'django_microsip_base.apps.plugins.django_msp_cotizador.django_msp_cotizador',
#     # 'django_microsip_base.apps.plugins.django_msp_facturaglobal.django_msp_facturaglobal',
#     # 'django_microsip_base.apps.plugins.django_msp_inventarios.django_msp_inventarios',
#     'django_microsip_base.apps.plugins.django_msp_organizador.django_msp_organizador',
#     # 'django_microsip_base.apps.plugins.django_msp_sms.django_msp_sms',
#     # 'django_microsip_base.apps.plugins.django_msp_polizas.django_msp_polizas',
#     # 'django_microsip_base.apps.plugins.django-microsip-liquida.django-microsip-liquida',
#     # 'django_msp_sms',
     

     
# )
extra_list = os.environ['SIC_INSTALLED_APPS'].split(',')
extra_list.remove('')
extra_list.remove('django-microsip-api')

EXTRA_MODULES = tuple(extra_list)

EXTRA_INFO = {
    'ruta_datos_facturacion': 'C:\sat',
}

MICROSIP_VERSION = 2014

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
