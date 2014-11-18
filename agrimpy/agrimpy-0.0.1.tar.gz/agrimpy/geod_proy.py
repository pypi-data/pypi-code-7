#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyproj
from gms_gyf import *

def config_proy(latitud_de_origen, meridiano_central, falso_este=0,
    falso_norte=0, factor_de_escala=1, datum='WGS84'):
    """Crea una proyeccion de tipo mercator transversal, con los siguientes
    parametros:
      latitud_de_origen     Latitud de origen
      meridiano_central     Meridiano central
      falso_este            Falso Este (0 por defecto, en metros)
      falso_norte           Falso Norte (0 por defecto, en metros)
      factor_de_escala      Factor de escala (1 por defecto)
      datum                 Datum, 'WGS84' por defecto (ver variable pj_ellps
      para otros datums posibles, ej: 'GRS80')
    """
    pmerct = pyproj.Proj(
        proj='tmerc',
        lat_0=latitud_de_origen,
        lon_0=meridiano_central,
        k=factor_de_escala,
        x_0=falso_este,
        y_0=falso_norte,
        ellps=datum)
    return pmerct


def proyGK(faja, datum='WGS84'):
    lat = -90
    lon = -(72 - (faja - 1) * 3)
    fe = faja * 1000000 + 500000
    fn = 0
    k = 1
    dat = datum
    return config_proy(lat, lon, fe, fn, k, dat)


def proy2geod(archivo_de_coordenadas, proyeccion, ext='geod', separador=','):
    """
    Wrapper de geod_proy con valores inv=True y file_ext='geod'
    """
    inv = True
    geod_proy(archivo_de_coordenadas, proyeccion, ext, inv, separador)


def geod2proy(archivo_de_coordenadas, proyeccion, ext='proy', separador=','):
    """
    Wrapper de geod_proy con valores inv=False y file_ext='proy'
    """
    inv = False
    geod_proy(archivo_de_coordenadas, proyeccion, ext, inv, separador)


def geod_proy(coord_file, proj, file_ext, inv, sep=','):
    """
    Transforaciones entre coordenadas geodesicas y planas proyectadas.
    Paramatros requeridos:
      coord_file: nombre del archivo de coordenadas
      proj:       proyección obtenida con la función 'config_proy'
      file_ext:   la extensión del archivo de salida
      inv (Bool): indica si la transformación va hacia un lado o hacia el otro
                  True: proy -> geod
                  False: geod -> proy
      sep: separador columnas del archivo de coordenadas (por defecto: ',')
    """
    # abrir los archivos de entrada y salida
    file_in = open(coord_file, 'r')
    file_out = open(coord_file + '.' + file_ext, 'a')
    # imprimir encabezado con info de proyección
    file_out.write('# Info de la proyeccion:\n#\t' + proj.srs + '\n')
    if inv:
        file_out.write('#id, lon (º \' "),\tlat (º \' ")\n')
    else:
        file_out.write('#id, E (m),\tN (m)\n')
    # recorrer archivo, transformar coordenadas y escribir archivo de salida
    for entry in file_in:
      if not entry.startswith('#') and entry.strip() != '' \
        and entry.find(sep) != -1:
          coord_id, coord_in1, coord_in2 = entry.split(sep)
          # tratamiento especial previo a la transformación
          if not inv:
              g1, m1, s1 = coord_in1.strip().split(' ')
              g2, m2, s2 = coord_in2.strip().split(' ')
              coord_in1 = gms2gyf(int(g1), int(m1), float(s1))
              coord_in2 = gms2gyf(int(g2), int(m2), float(s2))
          # transformación de las coordenadas
          coord_out1, coord_out2 = proj(coord_in1, coord_in2, inverse=inv)
          # tratamiento especial posterior a la transformación
          if inv:
              g1, m1, s1 = gyf2gms(coord_out1)
              g2, m2, s2 = gyf2gms(coord_out2)
              coord_out1 = str(g1) + ' ' + str(m1) + ' ' + str(s1)
              coord_out2 = str(g2) + ' ' + str(m2) + ' ' + str(s2)
          else:
              coord_out1 = round(coord_out1, 3)
              coord_out2 = round(coord_out2, 3)
          # escribir al archivo de salida las coordenadas transformadas
          file_out.write(str(coord_id) + sep + str(coord_out1) \
            + sep + str(coord_out2) + '\n')
    # cerrar los archivos
    file_in.close()
    file_out.close()

