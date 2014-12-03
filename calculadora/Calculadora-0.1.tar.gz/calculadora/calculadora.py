#encoding: utf-8
"""
Esta clase entrega la funcionalidad 
de una calculadora simple que puede 
sumar, retar, multiplcar y dividir.
"""

class Calculadora:
    """ Docstring de la clase Calculadora.
    
    Argumentos:
      opex (int): Primer operando entero.
      opey (int): Segundo operando entero.

    Attributes:
      x (int): Primer operando entero.
      y (int): Segundo operando entero.

    """

    def __init__(self, opex=0 , opey=0):
        """Constructor de la clase Calculadora"""
        self.asignar_x(opex)
        self.asignar_y(opey)

    def obtener_x(self):
        """Obtiene el valor del atributo x
            
        Argumentos:
          Ninguno

        Retorno:
          x (int): Primer operando entero

        """
        return self.x

    def asignar_x(self, valor):
        """Asigna un valor al atributo x

        Argumentos:
          valor (int): Número entero se asigna a x

        """
        self.x = valor

    def obtener_y(self):
        """Obtiene el valor del atributo y
            
        Argumentos:
          Ninguno

        Retorno:
          x (int): Primer operando entero

        """
        return self.y

    def asignar_y(self, valor):
        """Asigna un valor al atributo y

        Argumentos:
          valor (int): Número entero se asigna a y

        """
        self.y = valor

    def suma(self):
        """Calcula la suma de dos números.
            
        x + y 

        Devuelve un entero con la suma de dos numeros.

        Argumentos:
          Ninguno

        Ejemplos:

          >>> from calculadora import Calculadora

          >>> calc = Calculadora(3, 5)
          >>> print "Resultado", calc.suma()
          Resultado 8

          >>> calc = Calculadora()
          >>> calc.asignar_x(6)
          >>> calc.asignar_y(7)
          >>> print "Resultado", calc.add()
          Resultado 13

        """
        # Comentario de una línea
        return self.obtener_x() + self.obtener_y()

    def resta(self):
        """Calcula la resta de dos números.
            
        x - y 

        Devuelve un entero con la suma de dos numeros.

        Argumentos:
          Ninguno

        """
        # Comentario de una línea
        return self.obtener_x() - self.obtener_y()

    def multiplicacion(self):
        """Calcula la multiplicación de dos números.
            
        x * y 

        Devuelve un entero con la multiplicación de dos numeros.

        Argumentos:
          Ninguno

        """
        # Comentario de una línea
        return self.obtener_x() * self.obtener_y()

    def division(self):
        """Calcula la división de dos números.
            
        x / y 

        Devuelve un entero con la división de dos numeros.

        Argumentos:
          Ninguno

        Excepciones:
          ValueError -- Si (a == 0)

        """
        if self.y == 0:
            raise ValueError('El segundo operando no debe ser 0.')

        # Comentario de una línea
        return self.obtener_x() / self.obtener_y()