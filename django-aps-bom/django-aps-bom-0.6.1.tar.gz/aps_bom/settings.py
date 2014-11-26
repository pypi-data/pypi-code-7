"""Settings for the aps_bom app."""
from django.conf import settings
from django.core.urlresolvers import reverse_lazy

# default for the headlines in the csv file
BOM_CSV_FIELDNAMES = getattr(settings, 'APS_BOM_BOM_CSV_FIELDNAMES',
                             ["Position", "IPN", "Description", "QTY", "Unit",
                              "Shape"])

CBOM_CSV_FIELDNAMES = getattr(settings, 'APS_BOM_BOM_CSV_FIELDNAMES',
                              ["Position", "EPN", "Description", "QTY", "Unit",
                               "consign"])

BOM_UPLOAD_SUCCESS_URL = getattr(settings,
                                 'APS_BOM_BOM_UPLOAD_VIEW_SUCCESS_URL',
                                 reverse_lazy('aps_bom_bom_upload'))
