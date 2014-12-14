################################################################################
# CLASS    : Pattern
# PURPOSE  : generate a bit-sequence pattern
# AUTHOR   : Richard Booth
# DATE     : Sat Nov  9 11:23:03 2013
# -----------------------------------------------------------------------------
# NOTES    : 
#
# LICENSE  : (BSD-new)
# 
# This software is provided subject to the following terms and conditions,
# which you should read carefully before using the software.  Using this
# software indicates your acceptance of these terms and conditions.  If you
# do not agree with these terms and conditions, do not use the software.
# 
# Copyright (c) 2013 Richard Booth. All rights reserved.
# 
# Redistribution and use in source or binary forms, with or without
# modifications, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following Disclaimer
#       in each human readable file as well as in the documentation and/or
#       other materials provided with the distribution.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following Disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Richard Booth nor the names of contributors
#       (those who make changes to the software, documentation or other
#       materials) may be used to endorse or promote products derived from
#       this software without specific prior written permission.
# 
# Disclaimer
# 
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, INFRINGEMENT AND THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# ANY USE, MODIFICATION OR DISTRIBUTION OF THIS SOFTWARE IS SOLELY AT THE
# USERS OWN RISK.  IN NO EVENT SHALL RICHARD BOOTH OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, INCLUDING,
# BUT NOT LIMITED TO, CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
# IN NO EVENT SHALL THE AUTHORS OR DISTRIBUTORS BE LIABLE TO ANY PARTY
# FOR DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES
# ARISING OUT OF THE USE OF THIS SOFTWARE, ITS DOCUMENTATION, OR ANY
# DERIVATIVES THEREOF, EVEN IF THE AUTHORS HAVE BEEN ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# 
# THE AUTHORS AND DISTRIBUTORS SPECIFICALLY DISCLAIM ANY WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT.  THIS SOFTWARE
# IS PROVIDED ON AN "AS IS" BASIS, AND THE AUTHORS AND DISTRIBUTORS HAVE
# NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR
# MODIFICATIONS.
################################################################################
import user, decida
import string, re, math, random
from decida.ItclObjectx import ItclObjectx

class Pattern(ItclObjectx) :
    """ Pattern generator.

    **synopsis**:

    Pattern generates one of various bit-sequences and outputs the sequence
    as either a string of 1's and 0's, a piece-wise linear set of
    time, voltage pairs, or a set of time, binary pairs.

    The *Tckt* class uses *Pattern* to generate piece-wise linear voltage
    specifications for procedural simulation scripts.

    **constructor arguments**:

        .. option:: \*\*kwargs (dict)

              keyword=value specifications:
              configuration-options

    **configuration options**:

        .. option:: v0 (float, default=0.0)

              low value of the signal.

        .. option:: v1 (float, default=1.0)

              high value of the signal.

        .. option:: delay (float, default=0.0)

              delay before first bit.

        .. option:: edge (float, default=50ps)

              rise and fall times in s.

        .. option:: period (float, default=1ns)

              bit period in s.

        .. option:: pre (string, default="")

              specify preamble to bit-pattern (bit-sequence)

        .. option:: post (string, default="")

              specify suffix to bit-pattern (bit-sequence)

        .. option:: start_at_first_bit (bool, default=False)

              Normally a pwl sequence starts at the common-mode.
              If start_at_first_bit=True, start at first bit value.

        .. option:: format (string, default="pwl")

              Format of return list:

                "binary": return pattern only

                "time-binary": return list of time binary pairs

                "pwl": return piecewise linear waveform

    **example** (from test_Pattern): ::

        from decida.Pattern import Pattern
        
        p = Pattern(delay=4e-9, start_at_first_bit=True, edge=0.1e-9)
        pwl = p.prbs(length=50)
        print "t v"
        for t,v in zip(pwl[0::2], pwl[1::2]) :
            print t, v

    **public methods**:

        * public methods from *ItclObjectx*

    """
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Pattern main
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #==========================================================================
    # METHOD  : __init__
    # PURPOSE : constructor
    #==========================================================================
    def __init__(self, **kwargs) :
        ItclObjectx.__init__(self)
        #----------------------------------------------------------------------
        # private variables:
        #----------------------------------------------------------------------
        self.__poly = (
            "", " ", "", "1", "1", "1", "2", "5",
            "1", "432", "4", "3", "2", "641", "431", "531",
            "1", "532", "3", "521", "521", "3", "2",
            "1", "5", "431", "3", "621", "521", "3",
            "2", "641", "3", "75321", "641", "76521",
            "2", "65421", "54321", "651", "4", "543",
            "3", "54321", "643", "652", "431", "85321",
            "5", "75421", "654", "432", "631", "3",
            "621", "65432", "621", "742", "532", "651", "65431",
            "1", "521", "653", "1"
        )
        #----------------------------------------------------------------------
        # configuration options:
        #----------------------------------------------------------------------
        self._add_options({
            "v0"          : [0.0,    None],
            "v1"          : [1.0,    None],
            "delay"       : [0.0,    None],
            "edge"        : [50e-12, None],
            "period"      : [1e-9,   None],
            "pre"         : ["",     None],
            "post"        : ["",     None],
            "start_at_first_bit" : [False,  None],
            "format"      : ["pwl",  None],
        })
        #----------------------------------------------------------------------
        # keyword arguments are all configuration options
        #----------------------------------------------------------------------
        for key, value in kwargs.items() :
            self[key] = value
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Pattern configuration option callback methods
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Pattern user commands
    #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    #==========================================================================
    # METHOD  : pattern
    # PURPOSE : specify bit pattern directly
    #==========================================================================
    def pattern(self, pattern) :
        """ specify and generate a bit pattern directly.
    
        **arguments**:

            .. option:: pattern (string)

                a string of "1"'s and "0"'s
        
        **results**:

            * The *Pattern* pattern is set to the bit pattern.

            * Returns pattern in format specified by the *format*
              configuration option.
    
        """
        return self.format(pattern)
    #==========================================================================
    # METHOD : clock
    # PURPOSE : generate clock bit-sequence
    # ARGUMENTS :
    #   % length
    #       number of bits to generate
    #   % startbit (optional)
    #       first bit in the sequence; default=0
    #==========================================================================
    def clock(self, length, startbit=0) :
        """ generate clock pattern (0, 1, 0, 1, 0, ...).
    
        **arguments**:

            .. option:: length (int)

                The number of bits in the sequence

            .. option:: startbit (int, default=0)

                The starting bit of the bit sequence
        
        **results**:

            * The *Pattern* pattern is set to a clock pattern, with 
              the start bit set to the specified value.

            * Returns pattern in format specified by the *format*
              configuration option.
    
        """
        pattern = []
        bit = startbit
        for i in range(0, length) :
            bit = 1-bit
            pattern.append(str(bit))
        return self.format(string.join(pattern, ""))
    #==========================================================================
    # METHOD : long_short
    # PURPOSE : generate long 1/0 followed by clock 
    #==========================================================================
    def long_short(self, long, short, startbit=0) :
        """ generate a bit pattern with several repeated bits, followed by
            a phase where each bit is inverted.
    
        **arguments**:

            .. option:: long (int)

                number of bits in the long phase, where each bit
                is repeated.

            .. option:: short(int)

                number of bits in the short phase, where each bit
                is inverted.

            .. option:: startbit (int, default=0)

                The starting bit of the bit sequence

        **results**:

            * The *Pattern* pattern is set to the bit pattern.

            * Returns pattern in format specified by the *format*
              configuration option.
    
        """
        pattern = []
        bit = startbit
        for j in range(0, long) :
            pattern.append(str(bit))
        for j in range(0, short) :
            bit = 1 - bit
            pattern.append(str(bit))
        return self.format(string.join(pattern, ""))
    #==========================================================================
    # METHOD : rand
    # PURPOSE : generate random bit-sequence
    # ARGUMENTS :
    #   % length
    #       number of bits to generate
    #   % seed
    #       random seed (default = None)
    #==========================================================================
    def rand(self, length, seed=None) :
        """ generate a random bit sequence.
    
        **arguments**:

            .. option:: length (int)

                the length of the bit sequence.

            .. option:: seed (str, default=None)

                random seed to initialize random number generator.
        
        **results**:

            * The *Pattern* pattern is set to a random bit pattern.

            * Returns pattern in format specified by the *format*
              configuration option.
    
        """
        if seed :
            random.seed(seed)
        pattern = []
        for i in range(0, length) :
            bit = 1 if random.random() > 0.5 else 0
            pattern.append(str(bit))
        return self.format(string.join(pattern, ""))
    #==========================================================================
    # METHOD : prbs
    # ARGUMENTS :
    #==========================================================================
    def prbs(self, size=7, length=0) :
        """ generate a pseudo-random bit pattern.
    
        **arguments**:

            .. option:: size (int, default=7)

                The PRBS specification: size=7 generates a pseudo-random
                bit-sequence of length 2^7-1.

            .. option:: length (int, default=0)

                The length of the bit-sequence.  If length=0, generates
                a sequence of 2^size - 1.
        
        **results**:

            * The *Pattern* pattern is set to the PRBS bit pattern.

            * Returns pattern in format specified by the *format*
              configuration option.
    
        """
        taps = [int(x) for x in self.__poly[size]]
        if length < 1 :
            length = math.pow(2, size)
        register = [0] * size
        pattern  = []
        for i in range(0, length) :
            acc = register[-1] ^ 1
            pattern.append(str(acc))
            for tap in taps :
                acc = register[tap] ^ acc
            register.pop(-1)
            register.insert(0, acc)
        return self.format(string.join(pattern, ""))
    #==========================================================================
    # METHOD : format
    # ARGUMENTS :
    #   % pattern
    #       generated bit sequence
    #==========================================================================
    def format(self, pattern) :
        """ format the bit-sequence.
    
        **arguments**:

            .. option:: pattern (string)

                a string of "1"'s and "0"'s
        
        **results**:

            * Returns *Pattern* pattern in format specified by the *format*
              configuration option.

              format is one of:

                * "binary": string sequence of "1"'s and "0"'s

                * "time-binary": pairs of time, and integer value 1 or 0.

                * "pwl": pairs of time, value to account for signal
                  edge, period, and voltage low and high values.
    
        """
        pat = self["pre"] + pattern + self["post"]
        if   self["format"] == "binary" :
            return pat
        elif self["format"] == "time-binary" :
            time = 0.0
            olist = []
            for sbit in pat :
                olist.extend((time, int(sbit)))
                time += self["period"]
            return olist
        elif self["format"] == "pwl" :
            start = True
            time  = 0.0
            olist = []
            vcm   = (self["v1"] + self["v0"]) * 0.5
            for sbit in pat :
                vbit = self["v1"] if sbit == "1" else self["v0"]
                if start :
                    start = False
                    if self["start_at_first_bit"] :
                        if self["delay"] > 0.0:
                            olist.extend((time, vbit))
                            time += self["delay"]
                        olist.extend((time, vbit))
                    else :
                        if self["delay"] > 0.0:
                            olist.extend((time, vcm))
                            time += self["delay"]
                        olist.extend((time, vcm))
                        time += self["edge"]*0.5
                        olist.extend((time, vbit))
                else :
                    time += self["period"] - self["edge"]
                    olist.extend((time, vbit_1))
                    time += self["edge"]
                    olist.extend((time, vbit))
                vbit_1 = vbit
            return olist
