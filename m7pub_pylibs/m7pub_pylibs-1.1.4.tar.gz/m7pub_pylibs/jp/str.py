#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2014, MARIMORE Inc Tokyo, Japan.
# Contributed by 
#       Iqbal Abdullah <iqbal@marimore.co.jp>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, 
# are permitted provided that the following conditions are met:
#
#   *   Redistributions of source code must retain the above copyright notice, 
#       this list of conditions and the following disclaimer.
#   *   Redistributions in binary form must reproduce the above copyright notice, 
#       this list of conditions and the following disclaimer in the documentation 
#       and/or other materials provided with the distribution.
#   *   Neither the name of the MARIMORE Inc nor the names of its contributors 
#       may be used to endorse or promote products derived from this software 
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE 
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES 
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON 
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Utilities for ja strings
"""

__author__      = "Iqbal Abdullah <iqbal@marimore.co.jp>"
__date__        = "$LastChangedDate: 2011-01-15 11:22:39 +0900 (Sat, 15 Jan 2011) $"
__version__     = "$LastChangedRevision: 31 $"

import re

_ZENKAKAKU_KATAKANA = (u'ァ',u'ア',u'ィ,',u'イ',u'ゥ',u'ウ',u'ェ',u'エ',u'ォ',u'オ',u'カ',u'ガ',u'キ',u'ギ',u'ク',u'グ',u'ケ',u'ゲ',u'コ',u'ゴ',u'サ',u'ザ',u'シ',u'ジ',u'ス',u'ズ',u'セ',u'ゼ',u'ソ',u'ゾ',u'タ',u'ダ',u'チ',u'ヂ',u'ッ',u'ツ',u'ヅ',u'テ',u'デ',u'ト',u'ド',u'ナ',u'ニ',u'ヌ',u'ネ',u'ノ',u'ハ',u'バ',u'パ',u'ヒ',u'ビ',u'ピ',u'フ',u'ブ',u'プ',u'ヘ',u'ベ',u'ペ',u'ホ',u'ボ',u'ポ',u'マ',u'ミ',u'ム',u'メ',u'モ',u'ャ',u'ヤ',u'ュ',u'ユ',u'ョ',u'ヨ',u'ラ',u'リ',u'ル',u'レ',u'ロ',u'ヮ',u'ワ',u'ヰ',u'ヱ',u'ヲ',u'ン',u'ヴ',u'ヵ',u'ヶ',u'ー',) 


def is_only_fullwidth_katakana(s):
    """
    's' is a unicode string

    Returns True if 's' consists of all full-width katakana, False otherwise
    """

    for r in list(s):
        if r not in _ZENKAKAKU_KATAKANA:
            return False

    return True

#    regexp = re.compile(r'^(?:\xE3\x81[\x81-\xBF]|\xE3\x82[\x80-\x93])+$')
#    result = regexp.search(s)
#    if result != None:
#        return True
#    return False

