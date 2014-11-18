#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Funciones de conversión entre (grados, minutos, segundos) sexagesimales y
# grados y fracción.

from numpy import sign, trunc, abs


def gms2gyf(grados, minutos=0, segundos=0):
    """Conversion (gg,mm,ss.sssss) --> (g.frac)
    Por ejemplo:
        gms2gyf(-61,30)  = -61.5
        gms2gyf(0,-45)   = -0.75
        gms2gyf(-33)     = -33.0"""
    s = sign(grados)
    signo = 1 if s == 0 else s
    return signo * (signo * grados + minutos / 60.0 + segundos / 3600.0)


def gyf2gms(gyf):
    """Conversion (g.frac) --> (gg,mm,ss.sssss)
    Por ejemplo:
        gyf2gms(-61.5) = (-61,30,0.0)
        gyf2gms(-0.75) = (0,-45,0.0)"""
    # hacer las cuentas
    g = trunc(gyf)
    m = (gyf - g) * 60
    s = (m - trunc(m)) * 60
    # preparar la presentación
    g = int(g)
    m = int(m) if g == 0 else int(abs(m))
    s = abs(s) if m != 0 and g != 0 else s
    return (g, m, s)


def gyf2gms_list(gyf_list):
    """Conversion (g0.ggg,g1.ggg) --> ((g0,mm,ss.sss),(g1,mm,ss.sss)) masiva.
    Por ejemplo: gyf_list = [(-61.5,-31.456),(-63.456,31.3333),...]"""
    gms_list = []
    for i in gyf_list:
        gms_list.append((gyf2gms(i[0]), gyf2gms(i[1])))
    return gms_list


def gms2gyf_list(gms_list):
    """Conversion ((g0,mm,ss.sss),(g1,mm,ss.sss)) --> (g0.ggg,g1.ggg) masiva.
    Por ejemplo:
    gms_list = [((-61,30),(-31,45)),((-63,45),(31,20))]"""
    gyf_list = []
    for i in gms_list:
        gyf_list.append((gms2gyf(*i[0]), gms2gyf(*i[1])))
    return gyf_list

