# -*- coding: utf8 -*-

'''Computation of pH-values
Until now only water solutions are implemented!

Each (solved) solute will be instantiated as an instance of class Solute.
For computation of the titration curve an arbitrary number von acids and bases
is allowed.

Substances are identified either as a list of pK-values or
  (if in the dictionaries PKvalues_Acid or PKvalues_Base)
by their name or chemical formula. If the solute is uniquely identifiable, the
name can be abbreviated.

Example: Solute('caus') may be 'caustic soda' or 'caustic potash'.
  ('soda' or 'potash' may be better names)
  with Solute('caustic p') 'caustic potash' is uniquely identified.
  
Example:
from titration import *
acid = Solute('caustic p')
base = Solute('for')
titration = Titration(base,acid)
titration.plot_titration(3,1)

print(acid.name)
>>> caustic potash 
print(base.name)
>>> formic acid

Note: If a solute is identified by its name or formula, the program knows if
this solute is actually an acid or a base!

Author: Dieter Kadelka (2014/12/15), Email: DieterKadelka@aol.com
GNU General Public License (GPL)
'''

from __future__ import division

from scipy.interpolate import InterpolatedUnivariateSpline
from scipy.optimize import brentq
import matplotlib.pyplot as plt
from multi_key_dict import multi_key_dict

##################################################################
################ Voreinstellungen ################################

plot_precision = 1000   # Number of points for the titration curve
Temp = 25.0             # Temperature
#  Almost all acid- and base pK-values are only correct for an ambient temperature
#    of 25 degree Celsius
language = 'english'     # use english names

##################################################################
######################## Tables ##################################

##############  pK-values for acids (25° C) ######################
PKvalues_Acid = {
   'Trichloressigsäure':   [ 0.52,],
   'Benzolsulfonsäure':    [ 0.70,],
   'Jodsäure':             [ 0.77,],
   'schweflige Säure':     [ 1.81, 6.91],
   'chlorige Säure':       [ 2.00,],
   'Phosphorsäure':        [ 2.12, 7.21,12.68],
   'Chloressigsäure':      [ 2.85,],
   'Milchsäure':           [ 3.08,],
   'salpetrige Säure':     [ 3.37,],
   'Fluorwasserstoffsäure':[ 3.45,],
   'Ameisensäure':         [ 3.75,],
   'Benzoesäure':          [ 4.19,],
   'Essigsäure':           [ 4.75,],
   'Kohlensäure':          [ 6.37,10.25],
   'hypochlorige Säure':   [ 7.53,],
   'hypobromige Säure':    [ 8.69,],
   'Borsäure':             [ 9.14,],
   'Blausäure':            [ 9.31,],
   'Phenol':               [ 9.89,],
   'hypojodige Säure':     [10.64,],
   'Schwefelsäure':        [-1.00, 1.92], # the first value must not be too small
   'Oxalsäure':            [ 1.23, 4.19],
   'Phosphonsäure':        [ 2.00, 6.56],
   'Weinsäure':            [ 3.22, 4.82],
   'Schwefelwasserstoff':  [ 6.89,14.15],
   'Salpetersäure':        [-1.00,], # strong acid 
   'Salzsäure':            [-1.00,] # strong acid
  } 

############## pK-values for bases (25° C) #######################
PKvalues_Base = {
   'Harnstoff':            [13.90,],
   'Anilin':               [ 9.37,],
   'Pyridin':              [ 8.75,],
   'Hydroxylamin':         [ 7.97,],
   'Nikotin':              [ 5.98,],
   'Morphin':              [ 5.79,],
   'Hydrazin':             [ 5.77,],
   'Ammoniak':             [ 4.75,],
   'Trimethylamin':        [ 4.19,],
   'Methylamin':           [ 3.44,],
   'Dimethylamin':         [ 3.27,],
   'Ethylamin':            [ 3.19,],
   'Triethylamin':         [ 2.99,],
   'Natronlauge':          [-1.00,], # strong base
   'Kalilauge':            [-1.00,]  # strong base
 }  

Chemical_Formulas = {
   'Trichloressigsäure':   'CCl_3COOH',
   'Benzolsulfonsäure':    'C_6H_5SO_3H',
   'chlorige Säure':       'HClO_2',
   'Jodsäure':             'HJ',
   'Schwefelsäure':        'H_2SO_4',
   'schweflige Säure':     'H_2SO_3',
   'Kohlensäure':          'H_2CO_3',
   'salpetrige Säure':     'HNO_2',
   'Fluorwasserstoffsäure':'HF',
   'Blausäure':            'HCN',
   'Schwefelwasserstoff':  'H_2S',
   'Phosphonsäure':        'H_3PO_3',
   'Phosphorsäure':        'H_3PO_4',
   'Chloressigsäure':      'CH_2ClCOOH',
   'Milchsäure':           'CH_3CH(OH)COOH',
   'Ameisensäure':         'HCOOH',
   'Benzoesäure':          'C_6H_5COOH',
   'Essigsäure':           'CH_3COOH',
   'hypochlorige Säure':   'HClO',
   'hypobromige Säure':    'HBrO',
   'Borsäure':             'B(OH)_3',
   'Phenol':               'C_6H_5OH',
   'hypojodige Säure':     'HJO',
   'Harnstoff':            'CO(NH_2)_2',
   'Anilin':               'C_6H_5NH_2',
   'Pyridin':              'C_5H_5N',
   'Hydroxylamin':         'NH_2OH',
   'Nikotin':              'C_10H_14N_2',
   'Morphin':              'C_17H_19O_3N',
   'Hydrazin':             'NH_2NH_2',
   'Ammoniak':             'NH_3',
   'Trimethylamin':        '(CH_3)_3N',
   'Methylamin':           'CH_3NH_2',
   'Dimethylamin':         '(CH_3)_2NH',
   'Ethylamin':            'C_2H_5NH_2',
   'Triethylamin':         '(C_2H_5)_3N',
   'Natronlauge':          'NaOH',
   'Kalilauge':            'KOH',
   'Salzsäure':            'HCl',
   'Salpetersäure':        'HNO_3'
 }

English_Names = {
   'Trichloressigsäure':   'trichloroacetic acid',
   'Benzolsulfonsäure':    'Benzenesulfonic acid',
   'Jodsäure':             'hydrogen iodide',
   'schweflige Säure':     'sulfurous acid',
   'chlorige Säure':       'chlorous acid',
   'Phosphorsäure':        'phosphoric acid',
   'Chloressigsäure':      'chloracetic acid',
   'Milchsäure':           'lactic acid',
   'salpetrige Säure':     'nitrous acid',
   'Fluorwasserstoffsäure':'fluorhydric acid',
   'Ameisensäure':         'formic acid',
   'Benzoesäure':          'benzoic acid',
   'Essigsäure':           'acetic acid',
   'Kohlensäure':          'carbonic acid',
   'hypochlorige Säure':   'hypochlorous acid',
   'hypobromige Säure':    'hydroxidobromime',
   'Borsäure':             'boric acid',
   'Blausäure':            'hydrocyanic acid',
   'Phenol':               'phenol',
   'hypojodige Säure':     'hypoiodic acid',
   'Schwefelsäure':        'sulfuric acid',
   'Oxalsäure':            'oxalic acid',
   'Phosphonsäure':        'phosphonic acid', 
   'Weinsäure':            'tartaric acid',
   'Schwefelwasserstoff':  'hydrogen sulfid',
   'Salpetersäure':        'nitric acid',
   'Salzsäure':            'hydrochloric acid',
   'Harnstoff':            'urea',
   'Anilin':               'aniline',
   'Pyridin':              'pyridine',
   'Hydroxylamin':         'hydroxylamine',
   'Nikotin':              'nicotine',
   'Morphin':              'morphine',
   'Hydrazin':             'hydrazine',
   'Ammoniak':             'ammonia',
   'Trimethylamin':        'trimethylamine',
   'Methylamin':           'methylamine',
   'Dimethylamin':         'dimethylamine',
   'Ethylamin':            'ethylamine',
   'Triethylamin':         'triethylamine',
   'Natronlauge':          'caustic soda',
   'Kalilauge':            'caustic potash'
  }

Kvalues_Acid = multi_key_dict() 
for acid in PKvalues_Acid.keys():
  if acid in Chemical_Formulas:
    formula = Chemical_Formulas[acid]
    if language == 'english':
      english_acid = English_Names[acid]
      Kvalues_Acid[english_acid,formula] = [10**(-x) for x in PKvalues_Acid[acid]]
    else:  
      Kvalues_Acid[acid,formula] = [10**(-x) for x in PKvalues_Acid[acid]]
  else:
    if language == 'english':
      english_acid = English_Names[acid]
      Kvalues_Acid[english_acid] = [10**(-x) for x in PKvalues_Acid[acid]]
    else:  
      Kvalues_Acid[acid] = [10**(-x) for x in PKvalues_Acid[acid]]

Kvalues_Base = multi_key_dict() 
for base in PKvalues_Base.keys():
  if base in Chemical_Formulas:
    formula = Chemical_Formulas[base]
    if language == 'english':
      english_base = English_Names[base]
      Kvalues_Base[english_base,formula] = [10**(-x) for x in PKvalues_Base[base]]
    else:  
      Kvalues_Base[base,formula] = [10**(-x) for x in PKvalues_Base[base]]
  else:
    if language == 'english':
      english_base = English_Names[base]
      Kvalues_Base[english_base] = [10**(-x) for x in PKvalues_Base[base]]
    else:  
      Kvalues_Base[base] = [10**(-x) for x in PKvalues_Base[base]]

KeyList = set()
for key in list(Kvalues_Acid.keys())+list(Kvalues_Base.keys()):
  # in python3 Kvalues_Acid.keys() is a view, not a list
  for item in key:
    KeyList.add(item)
# KeyList contains the known acids and bases

def known_solutes():
  for name in sorted(KeyList):
    print(name+',  ')

##################################################################
############### KW depends on the temperature ####################
# Water
# ToDo: We need similar values for the pK-values

KWT = {0:0.114e-14, 10:0.681e-14, 20: 0.929e-14, 25: 1.008e-14, 30: 1.469e-14, 40: 2.919e-14, 50: 5.474e-14, 60: 9.610e-14}

##### KW-value dependent on temperature (default 25° C)
class KW_T(object):

  def __init__(self,werte=KWT):
    werte = sorted(werte.items())
    self.spline = InterpolatedUnivariateSpline([x for (x,y) in werte],[y for (x,y) in werte])

  def __call__(self,t):
    return float(self.spline(t))

# Example: Let f = KW_T()
# Then f(temperature) computes the KW-value of water for a temperature in the
#   range 0 .. 60 ° C.

##################################################################
########## Solute instantiates the solved solute ###########

class Solute(object):
  '''Defines the properties of a solute.'''

  def __init__(self,KS,CS=1,acid=True):
    '''The list [KS1,...,KSn] contains the K-values (not the pK-values) of the
    solute. This list can be replaced by the name or the formula of the solute,
    if these are known to the program.
    CS is the concentration of the solute in mol/L.
    acid = True or acid = False (if the solute is a base).'''

    # Try to identify the K-values with the name of the solute
    try:
      ks = KS.lower()
      # ergibt AttributeError, wenn kein String vorliegt
      n = len(ks.strip())
      # Überprüfe, ob genau ein Name in KeyList mit ks beginnt
      count = 0
      for item in KeyList:
        if item[:n].lower() == ks.strip():
          count += 1
          item_found = item
      if count == 0:
        if language == 'german':
          print("Substanz nicht gefunden!")
        else:
          print("Solute not found!")
        return
      elif count > 1 and ks[-1] != ' ':
        if language == 'german':
          print("Substanz nicht eindeutig identifizierbar!")
        else:
          print("Solute not (uniquely) identifiable!")
        return
      else:
        # ob eine Säure oder Base vorliegt, wird hier anhand des Namens bestimmt
        if ks[-1] == ' ':
          item_found = item_found[:n]
        # Beispiel: Bei 'HCl ' könnte neben 'HCl' auch 'HClO' und 'HClO_2' gefunden
        #   werden! Nur 'HCl' ist aber gesucht.
        self.item_found = item_found
        self.name = item_found # name eventuell von Interesse
        if acid:
          try:
            self.KS = Kvalues_Acid[item_found]
            self.acid = True
          except KeyError:
            self.KS = Kvalues_Base[item_found]
            self.acid = False
        else:
          try:
            self.KS = Kvalues_Base[item_found]
            self.acid = False
          except KeyError:
            self.KS = Kvalues_Acid[item_found]
            self.acid = True
    except AttributeError: # Solute not found by name. Use the list KS
      self.KS = KS
      self.acid = acid
      # if the solute is a base, acid = False must explicitely be set
      #   (this is only needed, if the solute is not identified by its name)

    self.n = len(self.KS) # Maximal number of H^+ resp. OH^- ions
    self.CS = CS
    self.volume = 0.0
    # needed for the computation of total_volume

  def set_volume(self,volume):
    '''This allows to change the volume of one solute (titration)'''
    self.volume = volume
    # volume of the substace. May be variable during a titration.
    self.solution.compute_total_volume()
    # Compute the total volume of the solution.
    # self.solution identifies the solution (instance of class Solution)
    # self is part of solution

  def __call__(self,ph):
    '''ph actual ph-value.
    This function returns the total charge (in mol/L) of the substace.'''
    
    concentration = 10**(-ph) # pH-value -> concentration
    proportion = self.volume/self.total_volume
    if not self.acid:
      concentration = self.solution.KW/concentration
      # For bases the pK-value must be transformed first
    actual = 1.0
    for ks in self.KS:
      actual = 1 + concentration*actual/ks
    actual = self.CS * proportion / actual
    charge = self.n*actual 
    for i in range(self.n-1,0,-1):
      actual *= concentration / self.KS[i]
      charge += i*actual
    return charge 

  def charge_amount(self,ph):
    '''ph actual ph-value.
    For a ph-value given and solute AH_2, this function returns the amount of
      AH_2, AH^-, A^{2-}
    Similarly for other solutes.''' 
    
    concentration = 10**(-ph) # PH-value -> concentration
    if not self.acid:
      concentration = self.solution.KW/concentration
      # For bases the pK-value must be transformed first
    actual = 1.0
    for ks in self.KS:
      actual = 1 + concentration*actual/ks
    actual = self.CS / actual
    amount = [actual]
    for i in range(self.n-1,-1,-1):
      actual *= concentration / self.KS[i]
      amount.append(actual)
    amount_sum = sum(amount) 
    amount = [single_amount/amount_sum for single_amount in amount]
    amount.reverse()
    return amount

  def plot_protionation(self):
    '''Plot of the amount of AH_2, AH^-, A^{2-} for acid AH_2 (example)
    in the pH-range 0 ... 14'''
    # This depends on the solute only 

    plt.figure()
    ph_values = [0.01*i for i in range(1401)]
    prot = {}
    for i in range(len(self.KS)+1):
      prot[i] = []
    for ph in ph_values:
      prot_values = self.charge_amount(ph)
      for i in range(len(self.KS)+1):
        prot[i].append(prot_values[i])
    for i in range(len(self.KS)+1):
      plt.plot(ph_values,prot[i])
    plt.grid(True)  
    plt.title('Protionation')
    plt.xlabel('pH')
    plt.ylabel('Proportion')
    plt.show()

##################################################################
class Solution(object):
  "Solution with solved solutes"

  def __init__(self,*solutes):
    '''Determines the solved solutes. These are instances of Solute.'''
    self.number_solutes = len(solutes)
    self.solutes = solutes
    for solute in solutes:
      solute.solution = self
    # Each solved solute must know the solution it belongs to  
    self.Temp = Temp
    self.kw = KW_T()
    self.KW = self.kw(Temp)
    # ToDo: Other solvents as water, other temperatures (here 25° C)

  def compute_total_volume(self):
    self.total_volume = sum((solute.volume for solute in self.solutes))
    for solute in self.solutes:
      solute.total_volume = self.total_volume
      # Each component must know the total volume 

  def set_Temp(self,temp):
    'calculates temperature dependent constants'

    self.Temp = temp
    self.KW = self.kw(temp)
 
  def f(self,ph):
    '''This function calculates the total charge of the solution dependent on pH-value ph.
    If f(ph) = 0, then ph is the pH-value of the solution.'''
    
    hplus = 10**(-ph)        # pH-Value -> [H^+]
    ohminus = self.KW/hplus  # pH-Value -> [OH^-]
    charge = hplus - ohminus # charge of H^+ and OH^-
    for solute in self.solutes:
      if solute.acid:
        charge -= solute(ph)
      else:
        charge += solute(ph)
    return charge    
   
  def PH(self):
    'Compute the pH-value of the solution.'

    return brentq(self.f,-2,16,xtol=1e-10) # tolerance 1e-10 should be sufficient
    # Compute a zero of function f with the Brent (1973) method for pH-values
    #   between -2 and 16. This zero is the unknown pH-value of the solution.

############# Special Cases ########################################
# Solutions with one solute

class Acid(Solution):

  def __init__(self,KAH,CA=1,Temp=25.0):
    acid = Solute(KAH,CS=CA)
    Solution.__init__(self,acid)
    self.set_Temp = Temp
    self.solutes[0].set_volume(1.0) # This value must be not zero

def PH_Acid(KAH,CA=1):
  return Acid(KAH,CA).PH()

class Base(Solution):

  def __init__(self,KBH,CB=1,Temp=25.0):
    base = Solute(KBH,CS=CB,acid=False)
    Solution.__init__(self,base)
    self.set_Temp = Temp
    self.solutes[0].set_volume(1.0)

def PH_Base(KBH,CB=1):
  return Base(KBH,CB).PH()

##################################################################

class Titration(Solution):
  '''Calculate and plot the titration curve for a solution with arbitrary many solutes.     The volume of one solute varies, the others are fixed.'''

  def __init__(self,to_titrate,*rest_solutes):
    '''Determines the solved solutes. These are instances of Solute.
       The volume of to_titrate varies, the volumes of the solutes in rest_solutes
       are fixed. These volumes are parameters of plot_titration'''
    solutes = [to_titrate]+list(rest_solutes)
    self.to_titrate = to_titrate
    self.rest_solutes = rest_solutes
    # to_titrate (one solute) is variable, all other solutes are fixed
    Solution.__init__(self,*solutes)
    self.precision = plot_precision
    self.delta = 1.0/plot_precision

  def compute_PH(self,V_titrate):
    '''Computes the pH-value, if V_titrate is the volume of to_titrate (variable).
    The remaining solutes are constant.'''
    self.to_titrate.set_volume(V_titrate)
    return self.PH()

  def plot_titration(self,max_to_titrate,*V_rest_solutes):
    '''Plot of the titration curve.
    The volume of to_titrate is variable in the range 0 ... max_to_titrate,
    *V_rest_solutes are the volumes of the remaining solutes. The volume
    of solutes must have the same order as in __init__!'''

    for i in range(len(self.rest_solutes)):  
      self.rest_solutes[i].set_volume(V_rest_solutes[i])
      # Determines the volume of the constant solutes.
    dd = max_to_titrate*self.delta
    xwerte = [dd*i for i in range(self.precision+1)]
    ywerte = [self.compute_PH(x) for x in xwerte]
    titration_line = plt.plot(xwerte,ywerte,color='r')
    plt.axhline(y=7,xmin=0,xmax=1,color='g')
    plt.axvline(x=V_rest_solutes[0]*self.rest_solutes[0].CS/self.to_titrate.CS,ymin=0,ymax=1,color='g')
    plt.axvline(x=2*V_rest_solutes[0]*self.rest_solutes[0].CS/self.to_titrate.CS,ymin=0,ymax=1,color='g')
    plt.xlabel('Concentration')
    plt.ylabel('pH')
    plt.grid(True)
    plt.title('Titration Curve')
    plt.show()

