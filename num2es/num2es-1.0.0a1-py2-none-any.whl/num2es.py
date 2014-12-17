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
    0: u"cero",
    1: u"uno",
    2: u"dos",
    3: u"tres",
    4: u"cuatro",
    5: u"cinco",
    6: u"seis",
    7: u"siete",
    8: u"ocho",
    9: u"nueve",
    10: u"diez",
    11: u"once",
    12: u"doce",
    13: u"trece",
    14: u"catorce",
    15: u"quince",
    16: u"dieciséis",
    17: u"diecisiete",
    18: u"dieciocho",
    19: u"diecinueve",
    20: u"veinte",
    21: u"veintiuno",
    22: u"veintidos",
    23: u"veintitrés",
    24: u"veinticuatro",
    25: u"veinticinco",
    26: u"veintiséis",
    27: u"veintisiete",
    28: u"veintiocho",
    29: u"veintinueve",
    30: u"treinta",
    40: u"cuarenta",
    50: u"cincuenta",
    60: u"sesenta",
    70: u"setenta",
    80: u"ochenta",
    90: u"noventa",
    100: u"cien",
    200: u"doscientos",
    300: u"trescientos",
    400: u"cuatrocientos",
    500: u"quinientos",
    600: u"seiscientos",
    700: u"setecientos",
    800: u"ochocientos",
    900: u"novecientos",
    1000: u"mil",
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
                    first_output += u" "
                first_output += u"millón" if first == "1" else u"millones"
                
                second_output = self.number_to_text(second, False)
                
                self.text = u"{0} {1}".format(first_output,
                                              second_output)
    
    def number_to_text(self, s, million):
        s = str(int(s))
        length = len(s)
        
        if s == "0":
            return u""
        
        if length == 1:
            if s == "1" and million:
                return u"un"
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
                L.insert(i + count, u".")
                count += 1
        return u"".join(L[::-1])
    
    def compose(self, *numbers):
        return u"".join([str(n) for n in numbers])
    
    def decompose(self, s):
        return [int(i) for i in s]
    
    def two_digits(self, number):
        number_int = int(number)
        
        if number_int == 0:
            return u""
        elif number_int in NUMBERS:
            return NUMBERS[number_int]
        else:
            a, b = self.decompose(number)
            if a > 0:
                return u"{0} y {1}".format(
                    NUMBERS[int(u"{0}{1}".format(a, 0))], NUMBERS[b]
                )
            else:
                return NUMBERS[b]
    
    def three_digits(self, number, million=False):
        if int(number) == 0:
            return u""
        else:
            a, b, c = self.decompose(number)
            two_digits = self.two_digits(self.compose(b, c))
            
            first = NUMBERS[a * 100]
            if a == 1 and two_digits:
                first += u"to"
            first += u" "
            
            if a == 0:
                first = u""
            elif million:
                if two_digits == u"uno":
                    two_digits = two_digits.replace(u"uno", u"ún")
                else:
                    two_digits = two_digits.replace(u"uno", u"ún")
                if two_digits:
                    two_digits += u" "
            
            return u"{0}{1}".format(first, two_digits)
    
    def four_digits(self, number):
        if int(number) == 0:
            return u""
        else:
            a, b, c, d = self.decompose(number)
            three_digits = self.three_digits(self.compose(b, c, d))
            first = u"{0}mil ".format(NUMBERS[a] + u" " if a > 1 else u"")
            return u"{0} {1} ".format(first, three_digits)
    
    def five_or_six_digits(self, number, length):
        if int(number) == 0:
            return u""
        else:
            decomposed_number = self.decompose(number)
            s = u""
            for i in range(length - 3):
                s += u"{" + unicode(i) + u"}"
            
            first = int(s.format(*decomposed_number[:length - 3]))
            
            if first == 0:
                return u""
            if first in NUMBERS:
                first = NUMBERS[first]
            else:
                if length == 5:
                    first = self.two_digits(str(first))
                elif length == 6:
                    first = self.three_digits(str(first))
            
            if decomposed_number[length - 4] == 1:
                original = first
                first = first.replace(u" uno", u" un")
                if first == original:
                    first = first.replace(u"uno", u"ún")
            
            return u"{0} mil {1} ".format(first,
                self.three_digits(
                    self.compose(*(decomposed_number[length - 3:]))
                )
            )
    
    def seven_digits(self, number):
        if int(number) == 0:
            return u""
        else:
            decomposed_number = self.decompose(number)
            a, rest = decomposed_number[0], decomposed_number[1:]
            
            return u"{0} {1} {2}".format(
                u"un" if a == 1 else NUMBERS[a],
                u"millón" if a == 1 else u"millones",
                self.five_or_six_digits(self.compose(*rest), 6)
            )
    
    def __str__(self):
        return self.text.replace(u"  ", u" ")
    
    def __len__(self):
        return len(self.text)

