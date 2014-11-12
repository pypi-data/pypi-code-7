# -*- coding: utf-8 -*-
#
#  engines.py
#  referredby
#

"""
Common and uncommon search engines, borrowed from Spiros Denaxas's
URI: : ParseSearchString project
(https: //github.com/spiros/URI-ParseSearchString).
"""

from collections import namedtuple
import re

EngineDef = namedtuple('EngineDef', 'name param')
MailDef = namedtuple('MailDef', 'name')

MAIL_RE = [
    (re.compile(r'.*\.mail\.yahoo\.(com|net)'), MailDef('Yahoo! Mail')),
    (re.compile(r'mail\.google\.com'), MailDef('Google Mail')),
    (re.compile(r'.*\.mail\.live\.com'), MailDef('Hotmail')),
]

SEARCH_EXACT = {
    'abacho.com': EngineDef('Abacho', 'q'),
    'acbusca.com': EngineDef('ACBusca', 'query'),
    'aeiou.pt': EngineDef('Aeiou', 'q'),
    'alice.it': EngineDef('Alice.it', 'qs'),
    'alltheweb.com': EngineDef('AllTheWeb', 'q'),
    'altavista.com': EngineDef('Altavista', 'q'),
    'answers.yahoo.com': EngineDef('Yahoo Answers', 'p'),
    'aolsearch.aol.com': EngineDef('AOL Search', 'query'),
    'as.starware.com': EngineDef('Starware', 'qry'),
    'ask.com': EngineDef('Ask dot com', 'q'),
    'atalhocerto.com.br': EngineDef('Atalho Certo', 'keyword'),
    'at.search.yahoo.com': EngineDef('Yahoo Austria', 'p'),
    'au.search.yahoo.com': EngineDef('Yahoo Australia', 'p'),
    'bastaclicar.com.br': EngineDef('Basta Clicar', 'search'),
    'bemrapido.com.br': EngineDef('Bem Rapido', 'chave'),
    'bing.com': EngineDef('Bing', 'q'),
    'blogs.icerocket.com': EngineDef('IceRocket', 'q'),
    'blogsearch.google.com': EngineDef('Google Blogsearch', 'q'),
    'blueyonder.co.uk': EngineDef('Blueyonder', 'q'),
    'br.altavista.com': EngineDef('AltaVista Brasil', 'q'),
    'br.search.yahoo.com': EngineDef('Yahoo Brazil', 'p'),
    'btjunkie.org': EngineDef('BT Junkie', 'q'),
    'busca.orange.es': EngineDef('Orange ES', 'buscar'),
    'busca.uol.com.br': EngineDef('Radar UOL', 'q'),
    'buscaaqui.com.br': EngineDef('Busca Aqui', 'q'),
    'buscador.lycos.es': EngineDef('Lycos ES', 'query'),
    'buscador.terra.com.br': EngineDef('Terra Busca', 'query'),
    'buscador.terra.es': EngineDef('Terra ES', 'query'),
    'buscar.ozu.es': EngineDef('Ozu ES', 'q'),
    'cade.search.yahoo.com': EngineDef('Cadê', 'p'),
    'categorico.it': EngineDef('Categorico IT', 'q'),
    'clickgratis.com.br': EngineDef('Click Gratis', 'query'),
    'clusty.com': EngineDef('Clusty', 'query'),
    'cn.bing.com': EngineDef('Bing China', 'q'),
    'community.paglo.com': EngineDef('Paglo', 'q'),
    'correiodamanha.pt': EngineDef('Correio da Manha', 'pesquisa'),
    'correiomanha.pt': EngineDef('Correio Manha', 'pesquisa'),
    'cuil.com': EngineDef('Cuil', 'q'),
    'cuil.pt': EngineDef('Cuil PT', 'q'),
    'dn.sapo.pt': EngineDef('Diario Noticias', 'Pesquisa'),
    'entrada.com.br': EngineDef('Entrada', 'q'),
    'excite.com': EngineDef('Excite', 'q'),
    'excite.it': EngineDef('Excite IT', 'q'),
    'fastbrowsersearch.com': EngineDef('Fastbrowsersearch', 'q'),
    'fastweb.it': EngineDef('Fastweb IT', 'q'),
    'feedster.com': EngineDef('Feedster', 'q'),
    'fotos.sapo.pt': EngineDef('SAPO fotos', 'word'),
    'gigabusca.com.br': EngineDef('Giga Busca', 'what'),
    'godado.com': EngineDef('Godado', 'key'),
    'godado.it': EngineDef('Godado (IT)', 'key'),
    'google.ad': EngineDef('Google Andorra', 'q'),
    'google.ae': EngineDef('Google United Arab Emirates', 'q'),
    'google.af': EngineDef('Google Afghanistan', 'q'),
    'google.ag': EngineDef('Google Antiqua and Barbuda', 'q'),
    'google.al': EngineDef('Google Albania', 'q'),
    'google.am': EngineDef('Google Armenia', 'q'),
    'google.as': EngineDef('Google American Samoa', 'q'),
    'google.at': EngineDef('Google Austria', 'q'),
    'google.az': EngineDef('Google Azerbaijan', 'q'),
    'google.ba': EngineDef('Google Bosnia and Herzegovina', 'q'),
    'google.be': EngineDef('Google Belgium', 'q'),
    'google.bf': EngineDef('Google Burkina Faso', 'q'),
    'google.bg': EngineDef('Google Bulgaria', 'q'),
    'google.bi': EngineDef('Google Burundi', 'q'),
    'google.bj': EngineDef('Google Benin', 'q'),
    'google.biz': EngineDef('Google dot biz', 'q'),
    'google.bo': EngineDef('Google Bolivia', 'q'),
    'google.bs': EngineDef('Google Bahamas', 'q'),
    'google.bt': EngineDef('Google Bhutan', 'q'),
    'google.by': EngineDef('Google Belarus', 'q'),
    'google.bz': EngineDef('Google Belize', 'q'),
    'google.ca': EngineDef('Google Canada', 'q'),
    'google.cc': EngineDef('Google Cocos Islands', 'q'),
    'google.cd': EngineDef('Google Dem Rep of Congo', 'q'),
    'google.cg': EngineDef('Google Rep of Congo', 'q'),
    'google.ch': EngineDef('Google Switzerland', 'q'),
    'google.ci': EngineDef('Google Cote dIvoire', 'q'),
    'google.cl': EngineDef('Google Chile', 'q'),
    'google.cm': EngineDef('Google Cameroon', 'q'),
    'google.cn': EngineDef('Google China', 'q'),
    'google.cv': EngineDef('Google Cape Verde', 'q'),
    'google.co.ao': EngineDef('Google Angola', 'q'),
    'google.co.at': EngineDef('Google Austria', 'q'),
    'google.co.bi': EngineDef('Google Burundi', 'q'),
    'google.co.bw': EngineDef('Google Botswana', 'q'),
    'google.co.ci': EngineDef('Google Ivory Coast', 'q'),
    'google.co.ck': EngineDef('Google Cook Islands', 'q'),
    'google.co.cr': EngineDef('Google Costa Rica', 'q'),
    'google.co.gg': EngineDef('Google Guernsey', 'q'),
    'google.co.gl': EngineDef('Google Greenland', 'q'),
    'google.co.gy': EngineDef('Google Guyana', 'q'),
    'google.co.hu': EngineDef('Google Hungary', 'q'),
    'google.co.id': EngineDef('Google Indonesia', 'q'),
    'google.co.il': EngineDef('Google Israel', 'q'),
    'google.co.im': EngineDef('Google Isle of Man', 'q'),
    'google.co.in': EngineDef('Google India', 'q'),
    'google.co.it': EngineDef('Google Italy', 'q'),
    'google.co.je': EngineDef('Google Jersey', 'q'),
    'google.co.jp': EngineDef('Google Japan', 'q'),
    'google.co.ke': EngineDef('Google Kenya', 'q'),
    'google.co.kr': EngineDef('Google South Korea', 'q'),
    'google.co.ls': EngineDef('Google Lesotho', 'q'),
    'google.co.ma': EngineDef('Google Morocco', 'q'),
    'google.co.mu': EngineDef('Google Mauritius', 'q'),
    'google.co.mw': EngineDef('Google Malawi', 'q'),
    'google.co.mz': EngineDef('Google Mozambique', 'q'),
    'google.co.nz': EngineDef('Google New Zeland', 'q'),
    'google.co.pn': EngineDef('Google Pitcairn Islands', 'q'),
    'google.co.th': EngineDef('Google Thailand', 'q'),
    'google.co.tt': EngineDef('Google Trinidad and Tobago', 'q'),
    'google.co.tz': EngineDef('Google Tanzania', 'q'),
    'google.co.ug': EngineDef('Google Uganda', 'q'),
    'google.co.uk': EngineDef('Google UK', 'q'),
    'google.co.uz': EngineDef('Google Uzbekistan', 'q'),
    'google.co.ve': EngineDef('Google Venezuela', 'q'),
    'google.co.vi': EngineDef('Google US Virgin Islands', 'q'),
    'google.co.za': EngineDef('Google  South Africa', 'q'),
    'google.co.zm': EngineDef('Google Zambia', 'q'),
    'google.co.zw': EngineDef('Google Zimbabwe', 'q'),
    'google.com': EngineDef('Google', 'q'),
    'google.com.af': EngineDef('Google Afghanistan', 'q'),
    'google.com.ag': EngineDef('Google Antiqua and Barbuda', 'q'),
    'google.com.ai': EngineDef('Google Anguilla', 'q'),
    'google.com.ar': EngineDef('Google Argentina', 'q'),
    'google.com.au': EngineDef('Google Australia', 'q'),
    'google.com.az': EngineDef('Google Azerbaijan', 'q'),
    'google.com.bd': EngineDef('Google Bangladesh', 'q'),
    'google.com.bh': EngineDef('Google Bahrain', 'q'),
    'google.com.bi': EngineDef('Google Burundi', 'q'),
    'google.com.bn': EngineDef('Google Brunei Darussalam', 'q'),
    'google.com.bo': EngineDef('Google Bolivia', 'q'),
    'google.com.br': EngineDef('Google Brazil', 'q'),
    'google.com.bs': EngineDef('Google Bahamas', 'q'),
    'google.com.bz': EngineDef('Google Belize', 'q'),
    'google.com.cn': EngineDef('Google China', 'q'),
    'google.com.co': EngineDef('Google', 'q'),
    'google.com.cu': EngineDef('Google Cuba', 'q'),
    'google.com.cy': EngineDef('Google Cyprus', 'q'),
    'google.com.do': EngineDef('Google Dominican Rep', 'q'),
    'google.com.ec': EngineDef('Google Ecuador', 'q'),
    'google.com.eg': EngineDef('Google Egypt', 'q'),
    'google.com.et': EngineDef('Google Ethiopia', 'q'),
    'google.com.fj': EngineDef('Google Fiji', 'q'),
    'google.com.ge': EngineDef('Google Georgia', 'q'),
    'google.com.gh': EngineDef('Google Ghana', 'q'),
    'google.com.gi': EngineDef('Google Gibraltar', 'q'),
    'google.com.gl': EngineDef('Google Greenland', 'q'),
    'google.com.gp': EngineDef('Google Guadeloupe', 'q'),
    'google.com.gr': EngineDef('Google Greece', 'q'),
    'google.com.gt': EngineDef('Google Guatemala', 'q'),
    'google.com.gy': EngineDef('Google Guyana', 'q'),
    'google.com.hk': EngineDef('Google Hong Kong', 'q'),
    'google.com.hn': EngineDef('Google Honduras', 'q'),
    'google.com.hr': EngineDef('Google Croatia', 'q'),
    'google.com.iq': EngineDef('Google Iraq', 'q'),
    'google.com.jm': EngineDef('Google Jamaica', 'q'),
    'google.com.jo': EngineDef('Google Jordan', 'q'),
    'google.com.kg': EngineDef('Google Kyrgyzstan', 'q'),
    'google.com.kh': EngineDef('Google Cambodia', 'q'),
    'google.com.ki': EngineDef('Google Kiribati', 'q'),
    'google.com.kw': EngineDef('Google Kuwait', 'q'),
    'google.com.kz': EngineDef('Google Kazakhstan', 'q'),
    'google.com.lb': EngineDef('Google Lebanon', 'q'),
    'google.com.lk': EngineDef('Google Sri Lanka', 'q'),
    'google.com.lv': EngineDef('Google Latvia', 'q'),
    'google.com.ly': EngineDef('Google Libya', 'q'),
    'google.com.mm': EngineDef('Google Myanmar', 'q'),
    'google.com.mt': EngineDef('Google Malta', 'q'),
    'google.com.mu': EngineDef('Google Mauritius', 'q'),
    'google.com.mw': EngineDef('Google Malawi', 'q'),
    'google.com.mx': EngineDef('Google Mexico', 'q'),
    'google.com.my': EngineDef('Google Malaysia', 'q'),
    'google.com.na': EngineDef('Google Namibia', 'q'),
    'google.com.nf': EngineDef('Google Norfolk Island', 'q'),
    'google.com.ng': EngineDef('Google Nigeria', 'q'),
    'google.com.ni': EngineDef('Google Nicaragua', 'q'),
    'google.com.np': EngineDef('Google Nepal', 'q'),
    'google.com.nr': EngineDef('Google Nauru', 'q'),
    'google.com.om': EngineDef('Google Oman', 'q'),
    'google.com.pa': EngineDef('Google Panama', 'q'),
    'google.com.pe': EngineDef('Google Peru', 'q'),
    'google.com.pg': EngineDef('Google PapuaNew Guinea', 'q'),
    'google.com.ph': EngineDef('Google Philipines', 'q'),
    'google.com.pk': EngineDef('Google Pakistan', 'q'),
    'google.com.pl': EngineDef('Google Poland', 'q'),
    'google.com.pr': EngineDef('Google Puerto Rico', 'q'),
    'google.com.pt': EngineDef('Google Portugal', 'q'),
    'google.com.py': EngineDef('Google Paraguay', 'q'),
    'google.com.qa': EngineDef('Google', 'q'),
    'google.com.ru': EngineDef('Google Russia', 'q'),
    'google.com.sa': EngineDef('Google Saudi Arabia', 'q'),
    'google.com.sb': EngineDef('Google Solomon Islands', 'q'),
    'google.com.sc': EngineDef('Google Seychelles', 'q'),
    'google.com.sg': EngineDef('Google Singapore', 'q'),
    'google.com.sl': EngineDef('Google Sierra Leone', 'q'),
    'google.com.sv': EngineDef('Google El Savador', 'q'),
    'google.com.tj': EngineDef('Google Tajikistan', 'q'),
    'google.com.tr': EngineDef('Google Turkey', 'q'),
    'google.com.tt': EngineDef('Google Trinidad and Tobago', 'q'),
    'google.com.tw': EngineDef('Google Taiwan', 'q'),
    'google.com.ua': EngineDef('Google Ukraine', 'q'),
    'google.com.uy': EngineDef('Google Uruguay', 'q'),
    'google.com.uz': EngineDef('Google Uzbekistan', 'q'),
    'google.com.vc': EngineDef('Google Saint Vincent and the Grenadines', 'q'),
    'google.com.ve': EngineDef('Google Venezuela', 'q'),
    'google.com.vi': EngineDef('Google US Virgin Islands', 'q'),
    'google.com.vn': EngineDef('Google Vietnam', 'q'),
    'google.com.ws': EngineDef('Google Samoa', 'q'),
    'google.cz': EngineDef('Google Czech Rep', 'q'),
    'google.de': EngineDef('Google Germany', 'q'),
    'google.dj': EngineDef('Google Djubouti', 'q'),
    'google.dz': EngineDef('Google Algeria', 'q'),
    'google.dk': EngineDef('Google Denmark', 'q'),
    'google.dm': EngineDef('Google Dominica', 'q'),
    'google.ec': EngineDef('Google Ecuador', 'q'),
    'google.ee': EngineDef('Google Estonia', 'q'),
    'google.es': EngineDef('Google Spain', 'q'),
    'google.fi': EngineDef('Google Finland', 'q'),
    'google.fm': EngineDef('Google Micronesia', 'q'),
    'google.fr': EngineDef('Google France', 'q'),
    'google.gd': EngineDef('Google Grenada', 'q'),
    'google.ge': EngineDef('Google Georgia', 'q'),
    'google.gf': EngineDef('Google French Guiana', 'q'),
    'google.gg': EngineDef('Google Guernsey', 'q'),
    'google.gl': EngineDef('Google Greenland', 'q'),
    'google.gm': EngineDef('Google Gambia', 'q'),
    'google.gp': EngineDef('Google Guadeloupe', 'q'),
    'google.gr': EngineDef('Google Greece', 'q'),
    'google.gy': EngineDef('Google Guyana', 'q'),
    'google.hk': EngineDef('Google Hong Kong', 'q'),
    'google.hn': EngineDef('Google Honduras', 'q'),
    'google.hr': EngineDef('Google Croatia', 'q'),
    'google.ht': EngineDef('Google Haiti', 'q'),
    'google.hu': EngineDef('Google Hungary', 'q'),
    'google.ie': EngineDef('Google Ireland', 'q'),
    'google.im': EngineDef('Google Isle of Man', 'q'),
    'google.in': EngineDef('Google India', 'q'),
    'google.info': EngineDef('Google dot info', 'q'),
    'google.iq': EngineDef('Google Iraq', 'q'),
    'google.is': EngineDef('Google Iceland', 'q'),
    'google.it': EngineDef('Google Italy', 'q'),
    'google.je': EngineDef('Google Jersey', 'q'),
    'google.jo': EngineDef('Google Jordan', 'q'),
    'google.jobs': EngineDef('Google dot jobs', 'q'),
    'google.jp': EngineDef('Google Japan', 'q'),
    'google.kg': EngineDef('Google Kyrgyzstan', 'q'),
    'google.ki': EngineDef('Google Kiribati', 'q'),
    'google.kz': EngineDef('Google Kazakhstan', 'q'),
    'google.la': EngineDef('Google Laos', 'q'),
    'google.li': EngineDef('Google Liechtenstein', 'q'),
    'google.lk': EngineDef('Google Sri Lanka', 'q'),
    'google.lt': EngineDef('Google Lithuania', 'q'),
    'google.lu': EngineDef('Google Luxembourg', 'q'),
    'google.lv': EngineDef('Google Latvia', 'q'),
    'google.ma': EngineDef('Google Morocco', 'q'),
    'google.md': EngineDef('Google Moldova', 'q'),
    'google.me': EngineDef('Google Montenegro', 'q'),
    'google.mg': EngineDef('Google Madagascar', 'q'),
    'google.mk': EngineDef('Google Macedonia', 'q'),
    'google.ml': EngineDef('Google Mali', 'q'),
    'google.mn': EngineDef('Google Mongolia', 'q'),
    'google.mobi': EngineDef('Google dot mobi', 'q'),
    'google.ms': EngineDef('Google Montserrat', 'q'),
    'google.mu': EngineDef('Google Mauritius', 'q'),
    'google.mv': EngineDef('Google Maldives', 'q'),
    'google.mw': EngineDef('Google Malawi', 'q'),
    'google.net': EngineDef('Google dot net', 'q'),
    'google.nf': EngineDef('Google Norfolk Island', 'q'),
    'google.ng': EngineDef('Google Nigeria', 'q'),
    'google.nl': EngineDef('Google Netherlands', 'q'),
    'google.no': EngineDef('Google Norway', 'q'),
    'google.nr': EngineDef('Google Nauru', 'q'),
    'google.nu': EngineDef('Google Niue', 'q'),
    'google.off.ai': EngineDef('Google Anguilla', 'q'),
    'google.ph': EngineDef('Google Philipines', 'q'),
    'google.pk': EngineDef('Google Pakistan', 'q'),
    'google.pl': EngineDef('Google Poland', 'q'),
    'google.pn': EngineDef('Google Pitcairn Islands', 'q'),
    'google.pr': EngineDef('Google Puerto Rico', 'q'),
    'google.ps': EngineDef('Google Palestine', 'q'),
    'google.pt': EngineDef('Google Portugal', 'q'),
    'google.ro': EngineDef('Google Romania', 'q'),
    'google.rs': EngineDef('Google Serbia', 'q'),
    'google.ru': EngineDef('Google Russia', 'q'),
    'google.rw': EngineDef('Google Rwanda', 'q'),
    'google.sc': EngineDef('Google Seychelles', 'q'),
    'google.se': EngineDef('Google Sweden', 'q'),
    'google.sg': EngineDef('Google Singapore', 'q'),
    'google.sh': EngineDef('Google Saint Helena', 'q'),
    'google.si': EngineDef('Google Slovenia', 'q'),
    'google.sk': EngineDef('Google Slovakia', 'q'),
    'google.sm': EngineDef('Google San Marino', 'q'),
    'google.sn': EngineDef('Google Senegal', 'q'),
    'google.so': EngineDef('Google Somalia', 'q'),
    'google.sr': EngineDef('Google Suriname', 'q'),
    'google.st': EngineDef('Google Sao Tome', 'q'),
    'google.td': EngineDef('Google Chad', 'q'),
    'google.tg': EngineDef('Google Togo', 'q'),
    'google.tk': EngineDef('Google Tokelau', 'q'),
    'google.tl': EngineDef('Google East Timor', 'q'),
    'google.tm': EngineDef('Google Turkmenistan', 'q'),
    'google.tn': EngineDef('Google Tunisia', 'q'),
    'google.to': EngineDef('Google Tonga', 'q'),
    'google.tp': EngineDef('Google East Timor', 'q'),
    'google.tt': EngineDef('Google Trinidad and Tobago', 'q'),
    'google.tv': EngineDef('Google Tuvalu', 'q'),
    'google.tw': EngineDef('Google Taiwan', 'q'),
    'google.ug': EngineDef('Google Uganda', 'q'),
    'google.us': EngineDef('Google US', 'q'),
    'google.uz': EngineDef('Google Uzbekistan', 'q'),
    'google.vg': EngineDef('Google British Virgin Islands', 'q'),
    'google.vn': EngineDef('Google Vietnam', 'q'),
    'google.vu': EngineDef('Google Vanuatu', 'q'),
    'google.ws': EngineDef('Google Samoa', 'q'),
    'googleadservices.com': EngineDef('Google Adwords', 'q'),
    'gps.virgin.net': EngineDef('Virgin Search', 'q'),
    'guruji.com': EngineDef('Guruji', 'q'),
    'hotbot.com': EngineDef('HotBot', 'query'),
    'id.search.yahoo.com': EngineDef('Yahoo! Indonesia', 'p'),
    'ilmotore.com': EngineDef('ilMotore', 'query'),
    'images.search.yahoo.com': EngineDef('Yahoo! Images', 'p'),
    'images.google.com': EngineDef('Google Images', 'q'),
    'in.gr': EngineDef('In GR', 'q'),
    'in.search.yahoo.com': EngineDef('Yahoo India', 'p'),
    'internetica.com.br': EngineDef('Internetica', 'busca'),
    'iol.pt': EngineDef('Pesquisa Iol', 'q'),
    'isohunt.com': EngineDef('Isohunt', 'ihq'),
    'ithaki.net': EngineDef('Ithaki', 'query'),
    'jn.sapo.pt': EngineDef('Jornal Noticias', 'Pesquisa'),
    'katatudo.com.br': EngineDef('KataTudo', 'q'),
    'kataweb.it': EngineDef('Kataweb IT', 'q'),
    'libero.it': EngineDef('Libero IT', 'query'),
    'lycos.it': EngineDef('Lycos IT', 'query'),
    'mahalo.com': EngineDef('Mahalo', 'search'),
    'mamma.com': EngineDef('Mamma', 'query'),
    'megasearching.net': EngineDef('Megasearching', 's'),
    'minasplanet.com.br': EngineDef('Minas Planet', 'term'),
    'mirago.co.uk': EngineDef('Mirago UK', 'qry'),
    'netscape.com': EngineDef('Netscape', 's'),
    'pathfinder.gr': EngineDef('Pathfinder GR', 'q'),
    'pesquisa.clix.pt': EngineDef('Pesquisa Clix', 'question'),
    'phantis.com': EngineDef('Phantis GR', 'q'),
    'publico.clix.pt': EngineDef('Publico', 'q'),
    'record.pt': EngineDef('Jornal Record', 'q'),
    'rediff.com': EngineDef('Rediff', 'MT'),
    'robby.gr': EngineDef('Robby GR', 'searchstr'),
    'rtp.pt': EngineDef('Rtp', 'search'),
    'sabores.sapo.pt': EngineDef('SAPO sabores', 'cxSearch'),
    'sapo.pt': EngineDef('Pesquisa SAPO', 'q'),
    'search.aol.co.uk': EngineDef('AOL UK', 'query'),
    'search.arabia.msn.com': EngineDef('MSN Arabia', 'q'),
    'search.bbc.co.uk': EngineDef('BBC Search', 'q'),
    'search.bablyon.com': EngineDef('Bablyon', 'q'),
    'search.conduit.com': EngineDef('Conduit', 'q'),
    'search.conduit.com': EngineDef('Conduit', 'q'),
    'search.icq.com': EngineDef('ICQ dot com', 'q'),
    'search.live.com': EngineDef('Live.com', 'q'),
    'search.lycos.co.uk': EngineDef('Lycos UK', 'query'),
    'search.lycos.com': EngineDef('Lycos', 'query'),
    'search.msn.co.uk': EngineDef('MSN UK', 'q'),
    'search.msn.com': EngineDef('MSN', 'q'),
    'search.myway.com': EngineDef('MyWay', 'searchfor'),
    'search.mywebsearch.com': EngineDef('My Web Search', 'searchfor'),
    'search.ntlworld.com': EngineDef('NTLWorld', 'q'),
    'search.orange.co.uk': EngineDef('Orange Search', 'q'),
    'search.prodigy.msn.com': EngineDef('MSN Prodigy', 'q'),
    'search.sweetim.com': EngineDef('Sweetim', 'q'),
    'search.virginmedia.com': EngineDef('VirginMedia', 'q'),
    'search.yahoo.co.jp': EngineDef('Yahoo Japan', 'p'),
    'search.yahoo.com': EngineDef('Yahoo!', 'p'),
    'search.yahoo.jp': EngineDef('Yahoo! Japan', 'p'),
    'simpatico.ws': EngineDef('Simpatico IT', 'query'),
    'soso.com': EngineDef('Soso', 'w'),
    'speedybusca.com.br': EngineDef('SpeedyBusca', 'q'),
    'sproose.com': EngineDef('Sproose', 'query'),
    'suche.fireball.de': EngineDef('Fireball DE', 'query'),
    'suche.t-online.de': EngineDef('T-Online', 'q'),
    'suche.web.de': EngineDef('Suche DE', 'su'),
    'technorati.com': EngineDef('Technorati', 'q'),
    'tesco.net': EngineDef('Tesco Search', 'q'),
    'thespider.it': EngineDef('TheSpider IT', 'q'),
    'tiscali.co.uk': EngineDef('Tiscali UK', 'query'),
    'torrentz.eu': EngineDef('Torrentz', 'f'),
    'uk.altavista.com': EngineDef('Altavista UK', 'q'),
    'uk.ask.com': EngineDef('Ask UK', 'q'),
    'uk.search.yahoo.com': EngineDef('Yahoo! UK', 'p'),
    'vaibuscar.com.br': EngineDef('Vai Busca', 'q'),
    'videos.sapo.pt': EngineDef('SAPO videos', 'word'),
    'xl.pt': EngineDef('XL', 'pesquisa'),
}

SEARCH_RE = [
    (re.compile(r'.*\.search\.yahoo\.com'), EngineDef('Yahoo!', 'p')),
]


def norm_domain(domain):
    "Normalise the domain name for use in later exact matches."
    if domain.startswith('www.') and len(domain) > 4:
        return domain[4:]

    return domain


def detect_search(domain):
    "Detect a search engine, or return None."
    if domain in SEARCH_EXACT:
        return SEARCH_EXACT[domain]

    normed = norm_domain(domain)
    if normed in SEARCH_EXACT:
        return SEARCH_EXACT[normed]

    for pattern, engine in SEARCH_RE:
        if pattern.match(domain):
            return engine


def detect_mail(domain):
    "Detect an email site, or return None."
    for pattern, maildef in MAIL_RE:
        if pattern.match(domain):
            return maildef


def detect_any(domain):
    "Detect a search engine or email site, or return None."
    return detect_search(domain) or detect_mail(domain)
