#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Pasos para transformar proy a geod/proy/GK y exportar a DXF

from geod_proy import *
from toDXF import *


#
# 1) Configurar Proyecciones usadas
#

# 1.1) Proyección Mercator Transversal cualquiera.
lat_orig = gms2gyf(-33,52)
merid_c = gms2gyf(-61,14)
pserapio = config_proy(lat_orig, merid_c)

# 1.2) Gauss-Kruger Faja 5
gk_faja5 = proyGK(5)


#
# 2) Transformar entre geodésicas y proyectadas
#

# 2.1) El proceso es proy -> geod -> proy -> geod. Si se comparan los archivos
#      de salida, deberían ser iguales entre ambas "proy" y ambas "geod".

# proy -> proy.geod
proy2geod('coord/proy', pserapio)
# proy.geod -> proy.geod.proy
geod2proy('coord/proy.geod', pserapio)
# proy.geod.proy -> proy.geod.proy.geod
proy2geod('coord/proy.geod.proy', pserapio)


#
# 3) Transformar entre geodésicas y proyectadas (GK-Faja5)
#

# 3.1) El proceso es geod -> gk5 -> geod -> gk5. Si se comparan los archivos de
#      salida, deberían ser iguales entre ambas "gk5" y ambas "geod".

# proy.geod -> proy.geod.gk5
geod2proy('coord/proy.geod', gk_faja5, 'gk5')
# proy.geod.gk5 -> proy.geod.gk5.geod
proy2geod('coord/proy.geod.gk5', gk_faja5)
# proy.geod.gk5.geod -> proy.geod.gk5.geod.gk5
geod2proy('coord/proy.geod.gk5.geod', gk_faja5, 'gk5')
# proy.geod.gk5.geod.gk5 -> proy.geod.gk5.geod.gk5.geod
proy2geod('coord/proy.geod.gk5.geod.gk5', gk_faja5)


#
# 4) Exportar a DXF
#

# Sólo tiene sentido mandar a DXF las coordenadas proyectadas.
coord2dxf('coord/proy')
coord2dxf('coord/proy.geod.proy')
coord2dxf('coord/proy.geod.gk5')
coord2dxf('coord/proy.geod.gk5.geod.gk5')

