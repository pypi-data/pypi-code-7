#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       num2es.py
#       
#       Copyright 2014 Francisco Vicent <franciscovicent@outlook.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#       
#       

NUMBERS = {
    0: "cero",
    1: "uno",
    2: "dos",
    3: "tres",
    4: "cuatro",
    5: "cinco",
    6: "seis",
    7: "siete",
    8: "ocho",
    9: "nueve",
    10: "diez",
    11: "once",
    12: "doce",
    13: "trece",
    14: "catorce",
    15: "quince",
    16: "dieciséis",
    17: "diecisiete",
    18: "dieciocho",
    19: "diecinueve",
    20: "veinte",
    21: "veintiuno",
    22: "veintidos",
    23: "veintitrés",
    24: "veinticuatro",
    25: "veinticinco",
    26: "veintiséis",
    27: "veintisiete",
    28: "veintiocho",
    29: "veintinueve",
    30: "treinta",
    40: "cuarenta",
    50: "cincuenta",
    60: "sesenta",
    70: "setenta",
    80: "ochenta",
    90: "noventa",
    100: "cien",
    200: "doscientos",
    300: "trescientos",
    400: "cuatrocientos",
    500: "quinientos",
    600: "seiscientos",
    700: "setecientos",
    800: "ochocientos",
    900: "novecientos",
    1000: "mil",
}


class TextNumber:
    
    def __init__(self, number):
        # Maximum number.
        assert number <= 999999999999
        
        self.number = number
        
        if self.number in NUMBERS:
            self.text = NUMBERS[self.number]
        else:
            s = str(self.number)
            length = len(s)
            
            if length >= 2 and length <= 6:
                self.text = self.number_to_text(s, False)
            elif length >= 7:
                first = s[:length - 6]
                second = s[length - 6:]
                
                first_output = self.number_to_text(first, True)
                if length < 9:
                    first_output += " "
                first_output += "millón" if first == "1" else "millones"
                
                second_output = self.number_to_text(second, False)
                
                self.text = "{0} {1}".format(first_output,
                                              second_output)
    
    def number_to_text(self, s, million):
        s = str(int(s))
        length = len(s)
        
        if s == "0":
            return ""
        
        if length == 1:
            if s == "1" and million:
                return "un"
            else:
                return NUMBERS[int(s)]
        elif length == 2:
            return self.two_digits(s)
        elif length == 3:
            return self.three_digits(s, million)
        elif length == 4:
            return self.four_digits(s)
        elif length == 5 or length == 6:
            return self.five_or_six_digits(s, length)
    
    def nice_repr(self):
        L = list(str(self.number))[::-1]
        count = 0
        for i, c in enumerate(L):
            if i > 0 and i < len(L) - count and i / 3. == i / 3:
                L.insert(i + count, ".")
                count += 1
        return "".join(L[::-1])
    
    def compose(self, *numbers):
        return "".join([str(n) for n in numbers])
    
    def decompose(self, s):
        return [int(i) for i in s]
    
    def two_digits(self, number):
        number_int = int(number)
        
        if number_int == 0:
            return ""
        elif number_int in NUMBERS:
            return NUMBERS[number_int]
        else:
            a, b = self.decompose(number)
            if a > 0:
                return "{0} y {1}".format(
                    NUMBERS[int("{0}{1}".format(a, 0))], NUMBERS[b]
                )
            else:
                return NUMBERS[b]
    
    def three_digits(self, number, million=False):
        if int(number) == 0:
            return ""
        else:
            a, b, c = self.decompose(number)
            two_digits = self.two_digits(self.compose(b, c))
            
            first = NUMBERS[a * 100]
            if a == 1 and two_digits:
                first += "to"
            first += " "
            
            if a == 0:
                first = ""
            elif million:
                if two_digits == "uno":
                    two_digits = two_digits.replace("uno", "ún")
                else:
                    two_digits = two_digits.replace("uno", "ún")
                if two_digits:
                    two_digits += " "
            
            return "{0}{1}".format(first, two_digits)
    
    def four_digits(self, number):
        if int(number) == 0:
            return ""
        else:
            a, b, c, d = self.decompose(number)
            three_digits = self.three_digits(self.compose(b, c, d))
            first = "{0}mil ".format(NUMBERS[a] + " " if a > 1 else "")
            return "{0} {1} ".format(first, three_digits)
    
    def five_or_six_digits(self, number, length):
        if int(number) == 0:
            return ""
        else:
            decomposed_number = self.decompose(number)
            s = ""
            for i in range(length - 3):
                s += "{" + str(i) + "}"
            
            first = int(s.format(*decomposed_number[:length - 3]))
            
            if first == 0:
                return ""
            if first in NUMBERS:
                first = NUMBERS[first]
            else:
                if length == 5:
                    first = self.two_digits(str(first))
                elif length == 6:
                    first = self.three_digits(str(first))
            
            if decomposed_number[length - 4] == 1:
                original = first
                first = first.replace(" uno", " un")
                if first == original:
                    first = first.replace("uno", "ún")
            
            return "{0} mil {1} ".format(first,
                self.three_digits(
                    self.compose(*(decomposed_number[length - 3:]))
                )
            )
    
    def seven_digits(self, number):
        if int(number) == 0:
            return ""
        else:
            decomposed_number = self.decompose(number)
            a, rest = decomposed_number[0], decomposed_number[1:]
            
            return "{0} {1} {2}".format(
                "un" if a == 1 else NUMBERS[a],
                "millón" if a == 1 else "millones",
                self.five_or_six_digits(self.compose(*rest), 6)
            )
    
    def __str__(self):
        return self.text.replace("  ", " ")
    
    def __len__(self):
        return len(self.text)

