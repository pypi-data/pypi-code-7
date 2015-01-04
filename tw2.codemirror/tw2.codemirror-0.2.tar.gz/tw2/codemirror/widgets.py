import os
import tw2.core as twc
import tw2.forms as twf
from markupsafe import Markup


__all__ = ['CodeMirrorWidget']


codemirror_js = twc.JSLink(
    modname=__name__,
    filename='static/lib/codemirror.js',
    fromTextArea=twc.js_function('CodeMirror.fromTextArea')
)
codemirror_css = twc.CSSLink(
    modname=__name__,
    filename='static/lib/codemirror.css',
)

_codemirror_css = twc.CSSLink(
    modname=__name__,
    filename='static/style.css',
)

codemirror_util_dir = twc.DirLink(
    modname=__name__,
    whole_dir=True,
    filename='static/lib/util/',
)

#TODO: Make addons programmatically usable
# codemirror_addons = dict(
#     (d, twc.DirLink(modname=__name__, filename=os.path.join('static/addon', d)))
#         for d in os.listdir(os.path.join(os.path.dirname(__file__), 'static/addon')))

codemirror_addons = {
    'display': {
        'placeholder': twc.JSLink(modname=__name__,
            filename='static/addon/display/placeholder.js'
        ),
        'fullscreen': twc.JSLink(modname=__name__, filename='static/addon/display/fullscreen.js',
            resources=[twc.CSSLink(modname=__name__, filename='static/addon/display/fullscreen.css')]
        ),
    },
}

codemirror_keymaps = dict(
    (f.rstrip('.js'), twc.JSLink(modname=__name__, filename=os.path.join('static/keymap', f)))
        for f in os.listdir(os.path.join(os.path.dirname(__file__), 'static/keymap')))

codemirror_modes = dict(
    (d, twc.JSLink(modname=__name__, filename=os.path.join('static/mode', d, d + '.js')))
        for d in os.listdir(os.path.join(os.path.dirname(__file__), 'static/mode')))

codemirror_themes = dict(
    (f.rstrip('.css'), twc.CSSLink(modname=__name__, filename=os.path.join('static/theme', f)))
        for f in os.listdir(os.path.join(os.path.dirname(__file__), 'static/theme')))


def mode_name(mode):
    '''Tries best-effortly to get the right mode name'''

    if mode:
        l = mode.lower()

        if l in ('java', ):
            return ('clike', 'text/x-java')
        if l in ('c', ):
            return ('clike', 'text/x-csrc')
        if l in ('c++', 'cxx'):
            return ('clike', 'text/x-c++src')
        if l in ('csharp', 'c#'):
            return ('clike', 'text/x-csharp')

        if l in ('sh', 'bash', ):
            return ('shell', 'text/x-sh')

        if l in codemirror_modes:
            return (l, None)

    return (None, None)


class CodeMirrorWidget(twf.TextArea):
#    template = "tw2.codemirror.templates.codemirror"

    # declare static resources here
    resources = [codemirror_js, codemirror_css, _codemirror_css]

    mode = twc.Param('The highlighting mode for CodeMirror', default=None)
    keymap = twc.Param('The keymap for CodeMirror', default=None)
    theme = twc.Param('The theme for CodeMirror', default=None)
    fullscreen = twc.Param('Whether to include the fullscreen editing addon', default=False)
    height_from_rows = twc.Param('Whether to set the CodeMirror height from the rows', default=True)
    options = twc.Param('CodeMirror configuration options, '
            'see http://codemirror.net/doc/manual.html#config for more info',
        default={})
    default_options = {
        # 'theme': 'default',
        # 'keymap': 'default',
        'indentUnit': 4,
        'lineWrapping': True,
        'lineNumbers': True,
        'autofocus': False,
    }

    # @classmethod
    # def post_define(cls):
    #     pass
    #     # put custom initialisation code here

    def prepare(self):
        super(CodeMirrorWidget, self).prepare()
        # put code here to run just before the widget is displayed
        self.safe_modify('resources')

        options = self.default_options.copy()
        if self.options:
            options.update(self.options)

        if self.placeholder:
            #options['placeholder'] = self.placeholder
            self.resources.append(codemirror_addons['display']['placeholder'])

        try:
            (mode, mime) = mode_name(self.mode)
            self.resources.append(codemirror_modes[mode])
            options['mode'] = mime or mode
        except KeyError:
            pass

        if self.keymap:
            try:
                self.resources.append(codemirror_keymaps[self.keymap])
                options['keymap'] = self.keymap
            except KeyError:
                pass

        if self.theme:
            try:
                self.resources.append(codemirror_themes[self.theme])
                options['theme'] = self.theme
            except KeyError:
                pass

        if self.height_from_rows and self.rows is not None:
            _css = twc.CSSSource(src=u'#%s + .CodeMirror {height: %dem;}' % (self.compound_id, self.rows))
            self.resources.append(_css)

        if self.fullscreen:
            self.resources.append(codemirror_addons['display']['fullscreen'])
            #TODO: Customizable keys
            options['extraKeys'] = {
                "F11": twc.js_callback('function(cm) {cm.setOption("fullScreen", !cm.getOption("fullScreen"));}'),
                "Esc": twc.js_callback('function(cm) {if (cm.getOption("fullScreen")) cm.setOption("fullScreen", false);}'),
            }
            _help_text = self.help_text
            self.help_text = 'Press F11 when cursor is in the editor to toggle full screen editing. ' \
                             'Esc can also be used to exit full screen editing.' \
                             + Markup('<br />') + (_help_text if _help_text else '')

        self.add_call(codemirror_js.fromTextArea(twc.js_function('document.getElementById')(self.compound_id), options))
