# -*- coding: utf8 -*-

'''Berechnung von pH-Werten bei Titration
Jede der vorkaommenden (gelösten) Substanzen wird als Instanz von class Substance
erzeugt. Dies erlaubt es, beliebig viele Säuren und Basen zu betrachten.
Bisher nur Lösungsmittel Wasser implementiert.

Substanzen können über eine Liste von K-Werten oder über ihren Namen identifiziert
werden. Solange die Substanz eindeutig identifizierbar ist, muss der Name nicht
komplett eingegeben werden.

Beispiel: Substance('Am') nicht eindeutig identifizierbar, kann Ameisensäure oder
  Ammoniak sein. Substance('Ame') identifiziert aber eindeutig Ameisensäure.
  
Example:
from titration import *
acid = Substance('Ame')
base = Substance('Nat')
titration = Titration(base,acid)
titration.plot_titration(3,1)

print(acid.name)
>>> Ameisensäure
print(base.name)
>>> Natronlauge
'''

from __future__ import division

from scipy.interpolate import InterpolatedUnivariateSpline
from scipy.optimize import brentq
import matplotlib.pyplot as plt
from multi_key_dict import multi_key_dict

##################################################################
################ Voreinstellungen ################################

plot_genauigkeit = 1000 # Anzahl Zwischenpunkte bei Titrationskurven
Temp = 25.0             # Umgebungstemperatur
# Fast alle Säuren-/Basenkonstanten sind nur für 25.0 C korrekt
language = 'german'     # verwendet werdne die deutschen Bezeichnungen

##################################################################
######################## Tabellen ################################

############## Säurekonstanten (25° C) ############################
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
   'Schwefelsäure':        [-1.00, 1.92], # der erste Wert darf nicht zu klein sein!
   'Oxalsäure':            [ 1.23, 4.19],
   'Phosphonsäure':        [ 2.00, 6.56],
   'Weinsäure':            [ 3.22, 4.82],
   'Schwefelwasserstoff':  [ 6.89,14.15],
   'Salpetersäure':        [-1.00,], # starke Säure
   'Salzsäure':            [-1.00,] # starke Säure
  } 

############## Basenkonstanten (25° C) ############################
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
   'Natronlauge':          [-1.00,], # starke Lauge
   'Kalilauge':            [-1.00,]  # starke Lauge
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
# KeyList enthält alle vorkommenden Säuren und Basen

def bekannte_stoffe():
  for name in sorted(KeyList):
    print(name+',  ')

##################################################################
############### Temperaturabhängigkeit von KW ####################
# Wasser (vermutlich muss auch die Temperatur der gelösten Stoffe berücksichtigt werden!)

KWT = {0:0.114e-14, 10:0.681e-14, 20: 0.929e-14, 25: 1.008e-14, 30: 1.469e-14, 40: 2.919e-14, 50: 5.474e-14, 60: 9.610e-14}

##### KW-Wert in Abhängigkeit von der Temperatur (Voreinstellung 25° C)
class KW_T(object):

  def __init__(self,werte=KWT):
    werte = sorted(werte.items())
    self.spline = InterpolatedUnivariateSpline([x for (x,y) in werte],[y for (x,y) in werte])

  def __call__(self,t):
    return float(self.spline(t))

# Sei z.B. f = KW_T()
# Danach bestimmt f(Temperatur) den KW-Wert von Wasser. Ersetzt man KWT durch
#   andere Werte, so kann z.B. KHCl temperaturabhängig ausgegeben werden.

##################################################################
############### Substance legt gelösten Stoff fest ###############

class Substance(object):
  '''Lege Eigenschaften einer Substanz fest. Die Bezeichnung einer Instanz sollte
  den Namen der Substanz festlegen.'''

  def __init__(self,KS,CS=1,acid=True):
    '''Legt die Gleichgewichtskonstanten [KS1,...,KSn] der Substanz,
    die Konzentration CS der Substanz fest.'''

    # Zuerst werden die K-Werte entweder über den Bezeichner der Substanz
    #   oder direkt über die eingegebene Liste identifiziert
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
        print("Substanz nicht gefunden!")
        return
      elif count > 1 and ks[-1] != ' ':
        print("Substanz nicht eindeutig identifizierbar!")
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
    except AttributeError:
      self.KS = KS
      self.acid = acid
      # Liegt eine Base vor, so muss explizit acid = False übegeben werden!

    self.n = len(self.KS) # Maximale Anzahl der H^+ bzw. OH^- Ionen
    self.CS = CS
    self.volume = 0.0
    # wird definiert, damit total_volume stets berechnet werden kann.

  def set_volume(self,volume):
    '''Der Aufruf dieser Funktion ist sinnvoll, wenn das Volumen nur eines
    Lösungsbestandteils geändert wird (etwa bei der Titration).'''
    self.volume = volume
    # Das Volumen des Lösungsbestandteils. Bei der Titration ist volume variabel.
    self.solution.compute_total_volume()
    # Neuberechnung des Gesamtvolumens für alle Komponenten der Lösung

  def __call__(self,ph):
    '''ph ist der getestete ph-Wert,
    self.volume ist das Volumen der Einzellösung (muss bekannt sein),
    total_volume das Gesamtvolumen (Summe aller Einzel-Volumina)'''
    
    concentration = 10**(-ph) # PH-Wert -> Konzentration
    proportion = self.volume/self.total_volume
    if not self.acid:
      concentration = self.solution.KW/concentration
      # Bei Basen muss der PK-Wert erst umgewandelt werden
    actual = 1.0
    for ks in self.KS:
      actual = 1 + concentration*actual/ks
    actual = self.CS * proportion / actual
    charge = self.n*actual 
    for i in range(self.n-1,0,-1):
      actual *= concentration / self.KS[i]
      charge += i*actual
    return charge 
    # Zurückgegeben wird die Ladungsmenge (in Mol/Liter) des aktuellen gelösten Stoffes

  def charge_amount(self,ph):
    '''ph ist der getestete ph-Wert.
    Ausgegeben werden für die unterschiedlich protionierten Modifikation
    der Säure/Base die Anteile (beginnend mit dem nicht protionierten Stoff)''' 
    
    concentration = 10**(-ph) # PH-Wert -> Konzentration
    if not self.acid:
      concentration = self.solution.KW/concentration
      # Bei Basen muss der PK-Wert erst umgewandelt werden
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
    '''geplottet werden für die unterschiedlich protionierten Modifikation
    der Säure/Base die Anteile in Abhängigkeit des pH-Wertes im Bereich 0 .. 14'''
    # Dies sind Substanz-Eigenschaften

    plt.figure()
    ph_werte = [0.01*i for i in range(1401)]
    prot = {}
    for i in range(len(self.KS)+1):
      prot[i] = []
    for ph in ph_werte:
      prot_values = self.charge_amount(ph)
      for i in range(len(self.KS)+1):
        prot[i].append(prot_values[i])
    for i in range(len(self.KS)+1):
      plt.plot(ph_werte,prot[i])
    plt.grid(True)  
    plt.title('Protionierung')
    plt.xlabel('pH')
    plt.ylabel('Proportion')
    plt.show()

##################################################################
class Solution(object):
  "Lösung mit gelösten Substanzen"

  def __init__(self,*substances):
    '''Legt die verwendeten Lösungen fest. Übergeben werden die Lösungen als
    Instanzen von Substance.'''
    self.number_substances = len(substances)
    self.substances = substances
    for substance in substances:
      substance.solution = self
    # Jeder Lösungsbestandteil muss wissen, zu welcher Lösung er gehört
    self.Temp = Temp
    self.kw = KW_T()
    self.KW = self.kw(Temp)
    # Voreingestellt 25.0 C und Wasser als Lösungsmittel (kann modifiziert werden)

  def compute_total_volume(self):
    self.total_volume = sum((substance.volume for substance in self.substances))
    for substance in self.substances:
      substance.total_volume = self.total_volume
      # In jeder Komponente der Lösung wird das Gesamtvolumen der Lösung gespeichert

  def set_Temp(self,temp):
    'Bestimmt Temperaturabhängige Konstanten'

    self.Temp = temp
    self.KW = self.kw(temp)
 
  def f(self,x):
    '''Bestimmungsgleichung für [H+] bei vorgegebenen VA,VB,CA und CB.
    Sie ergibt sich aus der Ladungsbilanz, wenn [B+],[OH-] und [A+] als Funktion von
    [H+] aufgelöst werden. x ist der PH-Wert, d.h. -lg([H+]).'''
    hplus = 10**(-x) # x PH-Wert -> [H+]
    ohminus = self.KW/hplus
    charge = hplus - ohminus # H^+ und OH^-
    for substance in self.substances:
      if substance.acid:
        charge -= substance(x)
      else:
        charge += substance(x)
    return charge    
    # Davon wird in __call__ die Nullstelle bestimmt. Ist f([H+]) = 0, so ist die
    #   Ladungsbilanzgleichung erfüllt.
   
  def PH(self):
    'Berechne pH-Wert der Lösung'

    return brentq(self.f,-2,16,xtol=1e-10)

############# Sonderfälle #############

class Saeure(Solution):

  def __init__(self,KAH,CA=1,Temp=25.0):
    acid = Substance(KAH,CS=CA)
    Solution.__init__(self,acid)
    self.set_Temp = Temp
    self.substances[0].set_volume(1.0)

def PH_Saeure(KAH,CA=1):
  return Saeure(KAH,CA).PH()

class Lauge(Solution):

  def __init__(self,KBH,CB=1,Temp=25.0):
    base = Substance(KBH,CS=CB,acid=False)
    Solution.__init__(self,base)
    self.set_Temp = Temp
    self.substances[0].set_volume(1.0)

def PH_Lauge(KBH,CB=1):
  return Lauge(KBH,CB).PH()

##################################################################

class Titration(Solution):
  "Bestimme Titrationskurve"

  def __init__(self,to_titrate,*rest_substances):
    '''Legt die zu erwendeten Lösungen fest. Übergeben werden die Lösungen als
    Instanzen von Substance.'''
    substances = [to_titrate]+list(rest_substances)
    self.to_titrate = to_titrate
    self.rest_substances = rest_substances
    # Bekannt sein muss, was variabel ist (to_titrate) und was fest ist
    Solution.__init__(self,*substances)
    # Plot-Routine zum Plotten der Titrationskurve
    #   jede Instanz erhält ein eigenes Fenster
    self.genauigkeit = plot_genauigkeit
    self.delta = 1.0/plot_genauigkeit

  def compute_PH(self,V_titrate):
    '''Berechnet den PH-Wert, wenn V_titrate des Stoffes vorliegen, mit dem
    titriert wird. Die übrigen Stoffe sind konstant.'''
    self.to_titrate.set_volume(V_titrate)
    return self.PH()

  def plot_titration(self,max_to_titrate,*V_rest_substances):
    '''Plotte Titrationskurve.
    Die Lösungsmenge to_titrate ist variabel von 0 ... max_to_titrate,
    die übrigen Lösungsmengen sind konstant und müssen !!!
    in derselben Reihenfolge wie bei Instatierung eingegeben werden!'''

    for i in range(len(self.rest_substances)):  
      self.rest_substances[i].set_volume(V_rest_substances[i])
      # Legt die Volumina der konstant bleibenden Lösungen fest
    dd = max_to_titrate*self.delta
    xwerte = [dd*i for i in range(self.genauigkeit+1)]
    ywerte = [self.compute_PH(x) for x in xwerte]
    titration_line = plt.plot(xwerte,ywerte,color='r')
    plt.axhline(y=7,xmin=0,xmax=1,color='g')
    plt.axvline(x=V_rest_substances[0]*self.rest_substances[0].CS/self.to_titrate.CS,ymin=0,ymax=1,color='g')
    plt.axvline(x=2*V_rest_substances[0]*self.rest_substances[0].CS/self.to_titrate.CS,ymin=0,ymax=1,color='g')
    plt.xlabel('Concentration')
    plt.ylabel('pH')
    plt.grid(True)
    plt.title('Titrationskurve')
    plt.show()

