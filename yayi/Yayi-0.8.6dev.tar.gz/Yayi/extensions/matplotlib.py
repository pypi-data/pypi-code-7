# -*- coding: UTF-8 -*-

# This file defines some useful functions around matplotlib

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.mlab as mlab
import random

from .. import YAYI


def get_new_fig_and_sub():
  """Utility function creating a figure and a subfigure"""
  fig = plt.figure()
  sub = fig.add_subplot(111)
  return fig, sub

def plot_image(x):
  """Plots as Yayi image"""
  fig = plt.figure()
  sub = fig.add_subplot(111)
  if(isinstance(x , YAYI.CORE.Image)):
    sub.imshow(YAYI.IO.image_to_numpy(x), cmap = cm.gray)
  else:
    sub.imshow(x, cmap = cm.gray)
  return plt



def sub_add_points(points, sub = None, cols = None, p_element = 'o'):
  """Adds a list of points to the given subfigure (or creates it if needed)"""
  f = None
  if(sub is None):
    f, sub = get_new_fig_and_sub()
  for l in points:
    if(cols is None):
      sub.plot(l, 'o', linestyle='none', color=(random.random(), random.random(), random.random()))
    else:
      if(points.index(l) >= len(cols)):
        c= cols[-1]
      else:
        c = cols[points.index(l)]
      sub.plot(l, 'o', linestyle='none', color=c)
    
  return sub, sub.get_figure()


def sub_add_lines(points, sub = None, cols = None, p_element = 'o'):
  f = None
  if(sub is None):
    f, sub = get_new_fig_and_sub()
  for l in points:
    if(cols is None):
      sub.plot(l, 'o', linestyle='-', color=(random.random(), random.random(), random.random()))
    else:
      if(points.index(l) >= len(cols)):
        c= cols[-1]
      else:
        c = cols[points.index(l)]
      sub.plot(l, 'o', linestyle='-', color=c)
    
  return sub, f
