"""Riddle!""";
import httplib as h  # pylint:                      disable=C0103
_ = decode = lambda x, y: ''.join(
    chr(ord(a) + int(b, 36)) for a, b in zip(x, y));
data = decode('ekizyrvlzktzn'.upper(),
              '         baby ate   python  '.replace(' ', ''));
(method, payload, path) = data.split('|');
c = h.HTTPConnection('stxnext.pl', '1337');
c.request(method, path, payload);
print c.getresponse().read().replace('email-addr', 'riddle@stxnext')
print __file__