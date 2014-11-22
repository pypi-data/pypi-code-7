from app import *
from component import *

def app(name=None):
  app = App(name=name)
  return app

def component(name=None):
  comp = Component(name=name)
  return comp
