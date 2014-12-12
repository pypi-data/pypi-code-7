#! /usr/bin/env python
# -*- coding=utf-8 -*-

import sys

s = u"""Clguba齚琠——恏髞耼 涪懔

麍渗泉鼗龔坚。

螗鼟泉鼗蜿翼。

爥肤泉鼗钘虣。

钘虣泉鼗鯙鼴。

譤輲泉鼗遙鑎。

垱圑泉鼗灾鯔。

馶憪赾踝寘搤。

騲鷦鵞鶆第鸚眡鈇硽赾齚馘，齆龘馶巈泙巌鼊握鮌。

龘搤骠釬譥蚜墌憶，坁噇鹅男鈋嚥搤巌蕮鵋。

蹒鉍陽钋珘馶沨，龘搤醈懐駪窉聚。

涙蝶酨寖謧龥珘，蚥鐨蝶顶龥龥珘螗蝧眡揂鯲蟬蕝。

木籯巌輯龘釬螒，雅齫鹅龘蝶 Clguba 齚筯。

鵋齆懭鐨州龘鵋，鹟龘鵞趈炃酴髽譚巍龘鐣龘鵋。

鐣蘉鹅蟅胐馔黫觖嶵鹅眡蟬蕝，崂泶鈋龘蝶龥齻鐨蟬蕝；駘齚黿籯。

館馘猫垱蝶龥珘滈鐌眡禟趰，讔麹輑蹒钋鬅魼硽！"""

d = {}
for c in (65, 97):
    for i in range(26):
        d[i+c] = (i+13) % 26 + c

a = [ord(i) for i in s]
b = []
for x in a:
    if(19968 <= x <= 40869):
        b.append(60837 - x)
    else:
        b.append(d.get(x, x))

#print ''.join(unichr(x).encode('gb18030') for x in b)
if sys.version_info >= (3,):
    print(''.join(chr(x) for x in b))
else:
    print(''.join(unichr(x) for x in b))
#EOF
