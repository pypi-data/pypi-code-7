# -*- coding: utf-8 -*-

"""
   New version of html.py module that works on/with Unicode.

"""

from dk.text import u8, unicode_repr
import types as _types
import htmlentitydefs as _h
import string as _s
from .css import css
_map = map

raw_string_encodings = ('utf-8', 'iso-8859-1')


INLINE_ELEMENTS = '''
   a abbr acronym b basefont bdo big br cite code dfn em font i img input
   kbd label q s samp select small span strike strong sub sup textarea tt
   u var applet button del iframe ins map object script'''.split()

BLOCKLEVEL_ELEMENTS = '''
   address blockquote center dir div dl fieldset form h1 h2 h3 h4 h5 h6
   hr isindex menu noframes noscript ol p pre table ul dd dt frameset
   li tbody td tfoot th thead tr applet button del iframe ins map object
   script
   '''.split()


class EscapedString(unicode):
    pass


def escape_char(unichar):
    if len(unichar) > 1 and (unichar[0] == '&' and unichar[-1] == ';'):
        return str(unichar)
    
    o = ord(unichar)
    t = _h.codepoint2name.get(o, o)
    if t == o:
        if 0 < t < 128:
            return str(unichar)
        else:
            return ''
    else:
        return '&' + t + ';'


def escaped_array(s):
    """Convert unicode string to list of ascii characters or
       entitydefs like &oslash; etc.
    """
    return [escape_char(ch) for ch in s]


def escape(s, enc=None):
    """Convert string s (potentially unicode) to a ascii string
       with entitydefs like &oslash; &aelig; etc.
    """
    if s is None:
        return ''
    if not isinstance(s, unicode):
        if enc is not None:
            s = s.decode(enc)
    return ''.join(escape_char(c) for c in s)


def u8escape(s):
    return escape(s,'u8')


def rawstr2unicode(s):
    for enc in raw_string_encodings:
        try:
            return unicode(s, enc)
        except UnicodeDecodeError:
            pass
    raise UnicodeError("Could not decode raw string.")


def normalize(v):
    """returns a stringified unicode version of v
    """
    if not isinstance(v, basestring):
        # all 'other' objects: call their __str__ method
        v = unicode(str(v))
    elif not isinstance(v, unicode):
        # str objects: try to find encoding
        v = rawstr2unicode(v)
    return v


def quote(v):
    '''
       >>> quote(u"Bjorn's")
       u'"Bjorn\\'s"'
       >>> quote(u'the "best"')
       u'"the &quot;best&quot;"'
    '''  # '
    if u'"' in v:
        v = v.replace(u'"', u'&quot;')
    return u'"%s"' % v


def norm_attr_name(a):
    """_foo_bar => _foo_bar,  class_ => class, max_height => max-height
       >>> norm_attr_name(u'class_')
       u'class'
       >>> norm_attr_name(u'z_index')
       u'z-index'
    """
    if a[0] == u'_':
        return a
    if a[-1] == u'_':
        a = a[:-1]
    return a.replace(u'_', u'-')
    

class xtag(object):
    """x(ml-style)tag: a tag without content or a closing tag.
       E.g. <br/> would be xtag('br')
       [2009-03-11] w3 validator complains that 4.01 loose should not use
                    <foo />  but <foo>.
    """
    def __init__(self, tag_name, **kw):
        self._attr = {}
        self._name = tag_name
        self._nlafter = ''

        for k, v in kw.items():
            self._attr[norm_attr_name(k)] = v

    def __getattr__(self, name):
        try:
            return self._attr[norm_attr_name(name)]
        except KeyError:
            raise AttributeError

    def __setattr__(self, name, value):
        name = norm_attr_name(name)
        if name.startswith('_'):
            object.__setattr__(self, name, value)
        elif name in self._attr:
            self._attr[name] = value
        elif hasattr(self, name):
            object.__setattr__(self, name, value)
        else:
            self._attr[name] = value

    def attributes(self):
        """return a string like key="val". """
        res = []
        for k, v in self._attr.items():
            if isinstance(v, css):
                v = str(v)

            v = normalize(v)
            if v:
                res.append(u' %s=%s' % (k, quote(escape(v))))
        return ''.join(res)

    def _flatten(self):
        yield self

    def flatten(self):
        yield self

    def __unicode__(self):
        return u'<' + self._name + self.attributes() + u'>'

    def __xxstr__(self):
        return unicode(self).encode('u8')

    def __repr__(self):
        return repr(unicode(self))


class stag(xtag):
    """s(ingle)tag
    """
    def __unicode__(self):
        return u'<' + self._name + self.attributes() + u'>'


class tag(xtag):
    """Regular tag: outputs an open tag with attributes, followed by its
       contents, followed by a closing tag.

       Attributes can be set either as keyword arguments in the constructor
       or by assigning to attributes of the object.

       Content can be any combination of items, iterables, and generators:

         >> table(tr(td(i) for i in range(5)), tr(td(i**i) for i in range(5)))

       NB: Attributes that conflict with Python keywords have an underline
       appended, e.g.:  mytag.class_ = ...
    """
    def __init__(self, tag_name, *content, **kw):
        xtag.__init__(self, tag_name, **kw)
        if len(content) == 1 and type(content[0]) == _types.GeneratorType:
            self._content = list(content[0])
        else:
            self._content = content

    def xcontent():
        def fget(self):
            return self._content

        def fset(self, v):
            self._content = v
        return locals()
    xcontent = property(**xcontent())

    def _flatten(self, lst):
        for item in lst:
            if isinstance(item, (str, unicode, int, long, float)):
                yield item
            elif isinstance(item, xtag):
                for subitem in item.flatten():
                    yield subitem
            else:
                try:
                    for subitem in self._flatten(iter(item)):
                        yield subitem
                except TypeError:
                    yield item

    def flatten(self, lst=None):
        if lst is None:
            lst = self._content
        yield self.open_tag()
        for item in self._flatten(lst):
            yield item
        yield self.close_tag()
        return
        
    def open_tag(self):
        return u'<' + self._name + self.attributes() + u'>'

    def close_tag(self):
        return u'</' + self._name + u'>' + self._nlafter
        
    def __unicode__(self):
        res = []
        for item in self.flatten():
            try:
                res.append(unicode_repr(item))
            except TypeError:
                # generator found for some reason
                print type(item), dir(item)
                raise
        return ''.join(res)


class opentag(tag):
    def flatten(self, lst=None):
        yield self.open_tag()


class closetag(tag):
    def flatten(self, lst=None):
        yield self.close_tag()


class text(tag):
    """text tag: outputs its contents without any tags around it. Useful
       for grouping at the top level.
    """
    def __init__(self, *content):
        super(text,self).__init__('text', *content)
        
    def flatten(self):
        return self._flatten(self._content)


class lines(text):
    """like text, except each item in content is separated with a <br> tag.
    """
    def flatten(self):
        content = []
        for c in self._content[:-1]:
            content.append(c)
            content.append('<br>')
        content.append(self._content[-1])
        return self._flatten(content)


class dtag(tag):
    """d(issappearing)tag: if the content is empty, i.e. self.content == ('',)
       this tag doesn't output anything at all. Useful for legends, table
       captions, etc.
    """
    def __unicode__(self):
        if self._content:
            if len(self._content) == 1 and self._content[0] == u'':
                return u''
            return super(dtag,self).__str__()
        else:
            return u''


def _add(a, b):
    t = {}
    t.update(a)
    t.update(b)
    return t


def mktag(name, _parent=tag, _nlafter=False, **attrs):
    class _tmp(_parent):
        def __init__(self, *content, **kw):
            _parent.__init__(self, name, *content, **_add(attrs, kw))
            self._nlafter = _nlafter and '\n' or ''
    _tmp.__name__ = name
    return _tmp


def mkxtag(name, **attrs):
    class _tmp(xtag):
        def __init__(self, **kw):
            xtag.__init__(self, name, **_add(attrs, kw))
    _tmp.__name__ = name
    return _tmp


def mkdtag(name, **attrs):
    return mktag(name, _parent=dtag, **attrs)


def mkstag(name):
    return mktag(name, _parent=stag)

doctype401strict = mkstag(
    '!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"\n'
    '    "http://www.w3.org/TR/html4/strict.dtd"')
doctype401transitional = mkstag(
    '!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"\n'
    '    "http://www.w3.org/TR/html4/loose.dtd"')
doctype401frameset = mkstag(
    '!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Frameset//EN"\n'
    '    "http://www.w3.org/TR/html4/frameset.dtd"')

doctype = doctype401strict


xtags = "br hr img input link col meta".split()

for t in xtags:
    globals()[t] = mkxtag(t)

tags = '''
  a abbr acronym address applet area b base bsefont bdo big blockquote
  body button center cite code colgroup dd dfn div dl dt em
  fieldset font form frame frameset h1 h2 h3 h4 h5 h6 head html i
  iframe ins kbd label li map menu nobr noframes noscript ol
  optgroup option p param pre q s samp small span strike strong sub
  sup table tbody td textarea tfoot th thead title tr tt u ul var
  '''.split()

_nlafter = '''
  blockquote body center div dl dt fieldset form frame h1 h2 h3 h4 h5 h6
  head html iframe legend li ol option p pre table tbody title tr ul
  col colgroup
  '''.split()

for t in tags:
    globals()[t] = mktag(t, tag, t in _nlafter)

dtags = "caption legend".split()

for t in dtags:
    globals()[t] = mkdtag(t)

# special case (del is a keyword)
del_ = mktag('del')
dir_ = mktag('dir')
object_ = mktag('object')

start = mkxtag('link', rel='start')
prev = mkxtag('link', rel='prev')
next = mkxtag('link', rel='next')
stylesheet = mkxtag('link', rel='stylesheet', type='text/css', media='screen')
nynorsk = mkxtag('link', rel='alternate', hreflang='nn', lang='nn')
bokmaal = mkxtag('link', rel='alternate', hreflang='nb', lang='nb')
norsk = mkxtag('link', rel='alternate', hreflang='no', lang='no')
english = mkxtag('link', rel='alternate', hreflang='en', lang='en')
pdf = mkxtag('link', rel='alternate', type='application/pdf', media='print')

script = mktag('script', type='text/javascript')
style = mktag('style', type='text/css')

text_input = mkxtag('input', type='text')
hidden_input = mkxtag('input', type='hidden')
password_input = mkxtag('input', type='password')
checkbox_input = mkxtag('input', type='checkbox')
radio_input = mkxtag('input', type='radio')
submit_button = mkxtag('input', type='submit')


class select(tag):
    def __init__(self, options, selected=None, **kw):
        if 'id' not in kw:
            kw['id'] = 'id_' + kw['name']
        super(select, self).__init__('select', **kw)
        self._options = None
        self.options = options
        if selected is not None:
            selected = u8(selected)
        content = []
        for k, v in self.options:
            if u8(k) == selected:
                opt = option(v, value=k, selected='selected')
            else:
                opt = option(v, value=k)
            content.append(opt)
        self._content = tuple(content)

    def options():
        def fset(self, options):
            if len(options) == 0:
                self._options = []
            else:
                first = options[0]
                
                if len(first) == 2 and not isinstance(first, basestring):
                    self._options = [(unicode_repr(k), unicode_repr(v))
                                     for (k,v) in options]
                else:
                    self._options = [(unicode_repr(o), unicode_repr(o))
                                     for o in options]

        def fget(self):
            return self._options
        return locals()
    options = property(**options())

    def selected():
        def fset(self, v):
            if v not in self.values:
                raise ValueError("Only valid options can be selected.")
            self._selected = v

        def fget(self):
            return self._selected
        return locals()
    selected = property(**selected())

    def values():
        def fget(self):
            return [k for (k,v) in self.options]
        return locals()
    values = property(**values())


class tabledesc(object):
    def __init__(self, *cols):
        self.cols = cols
        

def test_doctest():
    """
       >>> br()
       u'<br>'
       >>> div('hello', b('world'))
       u'<div>hello<b>world</b></div>\\n'
       >>> print select(options=[u'a', u'b'], name='foo')
       u'<select name="foo" id="id_foo"><option value="a">a</option>\\n<option value="b">b</option>\\n</select>'
    """
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
