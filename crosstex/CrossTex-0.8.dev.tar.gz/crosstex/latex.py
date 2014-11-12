_latex = {160: '{~}', 161: '{!`}', 162: '{\\not{c}}', 163: '{\\pounds}',
    167: '{\\S}', 168: '{\\"{}}', 169: '{\\copyright}', 172: '{\\neg}',
    173: '{\\-}', 175: '{\\={}}', 176: '{\\mbox{$^\\circ$}}',
    177: '{\\mbox{$\\pm$}}', 178: '{\\mbox{$^2$}}', 179: '{\\mbox{$^3$}}',
    180: "{\\'{}", 181: '{\\mbox{$\\mu$}}', 182: '{\\P}',
    183: '{\\mbox{$\\cdot$}}', 184: '{\\c{}}', 185: '{\\mbox{$^1$}}',
    191: '{?`}', 192: '{\\`A}', 193: "{\\'A}", 194: '{\\^A}', 195: '{\\~A}',
    196: '{\\"A}', 197: '{\\AA}', 198: '{\\AE}', 199: '{\\c{C}}', 200: '{\\`E}',
    201: "{\\'E}", 202: '{\\^E}', 203: '{\\"E}', 204: '{\\`I}', 205: "{\\'I}",
    206: '{\\^I}', 207: '{\\"I}', 209: '{\\~N}', 210: '{\\`O}', 211: "{\\'O}",
    212: '{\\^O}', 213: '{\\~O}', 214: '{\\"O}', 215: '{\\mbox{$\\times$}}',
    216: '{\\O}', 217: '{\\`U}', 218: "{\\'U}", 219: '{\\^U}', 220: '{\\"U}',
    221: "{\\'Y}", 223: '{\\ss}', 224: '{\\`a}', 225: "{\\'a}", 226: '{\\^a}',
    227: '{\\~a}', 228: '{\\"a}', 229: '{\\aa}', 230: '{\\ae}', 231: '{\\c{c}}',
    232: '{\\`e}', 233: "{\\'e}", 234: '{\\^e}', 235: '{\\"e}', 236: '{\\`\\i}',
    237: "{\\'\\i}", 238: '{\\^\\i}', 239: '{\\"\\i}', 241: '{\\~n}',
    242: '{\\`o}', 243: "{\\'o}", 244: '{\\^o}', 245: '{\\~o}', 246: '{\\"o}',
    247: '{\\mbox{$\\div$}}', 248: '{\\o}', 249: '{\\`u}', 250: "{\\'u}",
    251: '{\\^u}', 252: '{\\"u}', 253: "{\\'y}", 255: '{\\"y}', 38: '{\&}',
    8467: '{\\ell}', 949: '{$\\epsilon$}', 955: '{$\\lambda$}',
    952: '{$\\theta$}', 153: '{\\oe}', 305: '{\\i}'}

def to_latex(s):
    ls = ''
    for c in s:
        if ord(c) in _latex:
            ls += _latex[ord(c)]
        else:
            ls += c
    return ls
