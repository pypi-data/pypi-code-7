# -*- coding: utf-8 -*-
"""
    sphinx.domains.operation
    ~~~~~~~~~~~~~~~~~~~~~~~~

    The Operation domain.

    :copyright: Copyright 2014 by togakushi
    :license: BSD, see LICENSE for details.
"""

import re

from docutils import nodes
from docutils.parsers.rst import directives

from sphinx import addnodes
from sphinx.roles import XRefRole
from sphinx.locale import l_, _
from sphinx.domains import Domain, ObjType, Index
from sphinx.directives import ObjectDescription
from sphinx.util.nodes import make_refnode
from sphinx.util.compat import Directive
from sphinx.util.docfields import Field, TypedField


# REs for Operation signatures
op_sig_re = re.compile(
    r'''^ ([\w.]*\.)?            # class name(s)
          (\w+)  \s*             # thing name
          (?: \((.*)\)           # optional: arguments
          )? $                   # and nothing more
          ''', re.VERBOSE)


class OperationXRefRole(XRefRole):
    def process_link(self, env, refnode, has_explicit_title, title, target):
        refnode['op:command'] = env.temp_data.get('op:command')
        refnode['op:setting'] = env.temp_data.get('op:setting')
        refnode['op:install'] = env.temp_data.get('op:install')
        refnode['op:howto'] = env.temp_data.get('op:howto')
        if not has_explicit_title:
            title = title.lstrip('.')   # only has a meaning for the target
            target = target.lstrip('~') # only has a meaning for the title
            # if the first character is a tilde, don't display the command/class
            # parts of the contents
            if title[0:1] == '~':
                title = title[1:]
                dot = title.rfind('.')
                if dot != -1:
                    title = title[dot+1:]
        # if the first character is a dot, search more specific namespaces first
        # else search builtins first
        if target[0:1] == '.':
            target = target[1:]
            refnode['refspecific'] = True
        return title, target


class OperationCommand(Directive):
    """
    Directive to mark description of a new command.
    """

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        'platform': lambda x: x,
        'synopsis': lambda x: x,
        'reverse': lambda x: x,
        'noindex': directives.flag,
        'deprecated': directives.flag,
    }

    def run(self):
        env = self.state.document.settings.env
        comname = self.arguments[0].strip()
        noindex = 'noindex' in self.options
        env.temp_data['op:command'] = comname
        ret = []
        if not noindex:
            env.domaindata['op']['commands'][comname] = \
                (env.docname, self.options.get('synopsis', ''),
                 self.options.get('platform', ''), 'deprecated' in self.options)
            # make a duplicate entry in 'objects' to facilitate searching for
            # the command in OperationDomain.find_obj()
            env.domaindata['op']['objects'][comname] = (env.docname, 'command')
            targetnode = nodes.target('', '', ids=['command-' + comname],
                                      ismod=True)
            self.state.document.note_explicit_target(targetnode)
            # the platform and synopsis aren't printed; in fact, they are only
            # used in the modindex currently
            ret.append(targetnode)
            indextext = _('%s (command)') % comname
            inode = addnodes.index(entries=[('single', indextext,
                                             'command-' + comname, '')])
            ret.append(inode)

            ### 
            if 'reverse' in self.options:
                if self.options.get('platform', ''):
                    revname = '%s (%s)' % (self.options.get('reverse', ''), self.options.get('platform', ''))
                else:
                    revname = self.options.get('reverse', '')
                env.temp_data['op:reverse'] = revname
                env.domaindata['op']['reverses'][revname] = \
                    (env.docname, self.options.get('synopsis', ''),
                     None, 'deprecated' in self.options)
                env.domaindata['op']['objects'][revname] = (env.docname, 'reverse')
                targetnode = nodes.target('', '', ids=['reverse-' + revname],
                                          ismod=True)
                self.state.document.note_explicit_target(targetnode)
                ret.append(targetnode)
                indextext = _('%s (reverse)') % revname
                inode = addnodes.index(entries=[('single', indextext,
                                                 'reverse-' + revname, '')])
                ret.append(inode)

        return ret


class OperationCommandIndex(Index):
    """
    Index subclass to provide the Operation command index.
    """

    name = 'commandindex'
    localname = l_('Command Index')
    shortname = l_('Command')

    def generate(self, docnames=None):
        content = {}
        # list of all commands, sorted by command name
        commands = sorted(self.domain.data['commands'].iteritems(),
                         key=lambda x: x[0].lower())
        # sort out collapsable commands
        prev_comname = ''
        num_toplevels = 0
        for comname, (docname, synopsis, platforms, deprecated) in commands:
            entries = content.setdefault(comname[0].lower(), [])

            package = comname.split('.')[0]
            if package != comname:
                # it's a subentries
                if prev_comname == package:
                    # first subentries - make parent a group head
                    if entries:
                        entries[-1][1] = 1
                elif not prev_comname.startswith(package):
                    # subentries without parent in list, add dummy entry
                    entries.append([package, 1, '', '', '', '', ''])
                subtype = 2
                entriename = comname.split(package + '.', 1)[1]
            else:
                num_toplevels += 1
                subtype = 0
                entriename = comname

            qualifier = deprecated and _('Deprecated') or ''
            entries.append([entriename, subtype, docname,
                            'command-' + comname, platforms, qualifier, synopsis])
            prev_comname = comname

        # apply heuristics when to collapse modindex at page load:
        # only collapse if number of toplevel commands is larger than
        # number of submodules
        collapse = len(commands) - num_toplevels < num_toplevels

        # sort by first letter
        content = sorted(content.iteritems())

        return content, collapse


class OperationSetting(Directive):
    """
    Directive to mark description of a new setting.
    """

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        'platform': lambda x: x,
        'synopsis': lambda x: x,
        'reverse': lambda x: x,
        'noindex': directives.flag,
        'deprecated': directives.flag,
    }

    def run(self):

        env = self.state.document.settings.env
        setname = self.arguments[0].strip()
        noindex = 'noindex' in self.options
        env.temp_data['op:setting'] = setname
        ret = []
        if not noindex:
            env.domaindata['op']['settings'][setname] = \
                (env.docname, self.options.get('synopsis', ''),
                 self.options.get('platform', ''), 'deprecated' in self.options)
            # make a duplicate entry in 'objects' to facilitate searching for
            # the command in OperationDomain.find_obj()
            env.domaindata['op']['objects'][setname] = (env.docname, 'setting')
            targetnode = nodes.target('', '', ids=['setting-' + setname],
                                      ismod=True)
            self.state.document.note_explicit_target(targetnode)
            # the platform and synopsis aren't printed; in fact, they are only
            # used in the modindex currently
            ret.append(targetnode)
            indextext = _('%s (setting)') % setname
            inode = addnodes.index(entries=[('single', indextext,
                                             'setting-' + setname, '')])
            ret.append(inode)

            ### 
            if 'reverse' in self.options:
                if self.options.get('platform', ''):
                    revname = '%s (%s)' % (self.options.get('reverse', ''), self.options.get('platform', ''))
                else:
                    revname = self.options.get('reverse', '')
                env.temp_data['op:reverse'] = revname
                env.domaindata['op']['reverses'][revname] = \
                    (env.docname, self.options.get('synopsis', ''),
                     None, 'deprecated' in self.options)
                env.domaindata['op']['objects'][revname] = (env.docname, 'reverse')
                targetnode = nodes.target('', '', ids=['reverse-' + revname],
                                          ismod=True)
                self.state.document.note_explicit_target(targetnode)
                ret.append(targetnode)
                indextext = _('%s (reverse)') % revname
                inode = addnodes.index(entries=[('single', indextext,
                                                 'reverse-' + revname, '')])
                ret.append(inode)

        return ret


class OperationSettingIndex(Index):
    """
    Index subclass to provide the Operation Seting index.
    """

    name = 'settingindex'
    localname = l_('Setting Index')
    shortname = l_('Setting')

    def generate(self, docnames=None):
        content = {}
        # list of all setting, sorted by setting name
        settings = sorted(self.domain.data['settings'].iteritems(),
                         key=lambda x: x[0].lower())
        # sort out collapsable setting
        prev_setname = ''
        num_toplevels = 0
        for setname, (docname, synopsis, platforms, deprecated) in settings:
            entries = content.setdefault(setname[0].lower(), [])

            package = setname.split('.')[0]
            if package != setname:
                # it's a subentries
                if prev_setname == package:
                    # first subentries - make parent a group head
                    if entries:
                        entries[-1][1] = 1
                elif not prev_setname.startswith(package):
                    # subentries without parent in list, add dummy entry
                    entries.append([package, 1, '', '', '', '', ''])
                subtype = 2
                entriename = setname.split(package + '.', 1)[1]
            else:
                num_toplevels += 1
                subtype = 0
                entriename = setname

            qualifier = deprecated and _('Deprecated') or ''
            entries.append([entriename, subtype, docname,
                            'setting-' + setname, platforms, qualifier, synopsis])
            prev_setname = setname

        # apply heuristics when to collapse modindex at page load:
        # only collapse if number of toplevel setting is larger than
        # number of subsetting
        collapse = len(settings) - num_toplevels < num_toplevels

        # sort by first letter
        content = sorted(content.iteritems())

        return content, collapse


class OperationInstall(Directive):
    """
    Directive to mark description of a new install.
    """

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        'platform': lambda x: x,
        'synopsis': lambda x: x,
        'reverse': lambda x: x,
        'noindex': directives.flag,
        'deprecated': directives.flag,
    }

    def run(self):
        env = self.state.document.settings.env
        insname = self.arguments[0].strip()
        noindex = 'noindex' in self.options
        env.temp_data['op:install'] = insname
        ret = []
        if not noindex:
            env.domaindata['op']['installs'][insname] = \
                (env.docname, self.options.get('synopsis', ''),
                 self.options.get('platform', ''), 'deprecated' in self.options)
            # make a duplicate entry in 'objects' to facilitate searching for
            # the install in OperationDomain.find_obj()
            env.domaindata['op']['objects'][insname] = (env.docname, 'install')
            targetnode = nodes.target('', '', ids=['install-' + insname],
                                      ismod=True)
            self.state.document.note_explicit_target(targetnode)
            # the platform and synopsis aren't printed; in fact, they are only
            # used in the modindex currently
            ret.append(targetnode)
            indextext = _('%s (install)') % insname
            inode = addnodes.index(entries=[('single', indextext,
                                             'install-' + insname, '')])
            ret.append(inode)

            ### 
            if 'reverse' in self.options:
                if self.options.get('platform', ''):
                    revname = '%s (%s)' % (self.options.get('reverse', ''), self.options.get('platform', ''))
                else:
                    revname = self.options.get('reverse', '')
                env.temp_data['op:reverse'] = revname
                env.domaindata['op']['reverses'][revname] = \
                    (env.docname, self.options.get('synopsis', ''),
                     None, 'deprecated' in self.options)
                env.domaindata['op']['objects'][revname] = (env.docname, 'reverse')
                targetnode = nodes.target('', '', ids=['reverse-' + revname],
                                          ismod=True)
                self.state.document.note_explicit_target(targetnode)
                ret.append(targetnode)
                indextext = _('%s (reverse)') % revname
                inode = addnodes.index(entries=[('single', indextext,
                                                 'reverse-' + revname, '')])
                ret.append(inode)
        return ret


class OperationInstallIndex(Index):
    """
    Index subclass to provide the Operation install index.
    """

    name = 'installindex'
    localname = l_('Install Index')
    shortname = l_('Install')

    def generate(self, docnames=None):
        content = {}
        # list of all installs, sorted by install name
        installs = sorted(self.domain.data['installs'].iteritems(),
                         key=lambda x: x[0].lower())
        # sort out collapsable installs
        prev_insname = ''
        num_toplevels = 0
        for insname, (docname, synopsis, platforms, deprecated) in installs:
            entries = content.setdefault(insname[0].lower(), [])

            package = insname.split('.')[0]
            if package != insname:
                # it's a subentries
                if prev_insname == package:
                    # first subentries - make parent a group head
                    if entries:
                        entries[-1][1] = 1
                elif not prev_insname.startswith(package):
                    # subentries without parent in list, add dummy entry
                    entries.append([package, 1, '', '', '', '', ''])
                subtype = 2
                entriename = insname.split(package + '.', 1)[1]
            else:
                num_toplevels += 1
                subtype = 0
                entriename = insname

            qualifier = deprecated and _('Deprecated') or ''
            entries.append([entriename, subtype, docname,
                            'install-' + insname, platforms, qualifier, synopsis])
            prev_insname = insname

        # apply heuristics when to collapse modindex at page load:
        # only collapse if number of toplevel installs is larger than
        # number of submodules
        collapse = len(installs) - num_toplevels < num_toplevels

        # sort by first letter
        content = sorted(content.iteritems())

        return content, collapse


class OperationReverseIndex(Index):
    """
    Index subclass to provide the Operation reverse index.
    """

    name = 'reverseindex'
    localname = l_('Reverse Index')
    shortname = l_('Reverse')

    def generate(self, docnames=None):
        content = {}
        # list of all reverses, sorted by reverse name
        reverses = sorted(self.domain.data['reverses'].iteritems(),
                         key=lambda x: x[0].lower())
        # sort out collapsable reverses
        prev_revname = ''
        num_toplevels = 0
        for revname, (docname, synopsis, platforms, deprecated) in reverses:
            entries = content.setdefault(revname[0].lower(), [])

            package = revname.split('.')[0]
            if package != revname:
                # it's a subentries
                if prev_revname == package:
                    # first subentries - make parent a group head
                    if entries:
                        entries[-1][1] = 1
                elif not prev_revname.startswith(package):
                    # subentries without parent in list, add dummy entry
                    entries.append([package, 1, '', '', '', '', ''])
                subtype = 2
                entriename = revname.split(package + '.', 1)[1]
            else:
                num_toplevels += 1
                subtype = 0
                entriename = revname

            qualifier = deprecated and _('Deprecated') or ''
            entries.append([entriename, subtype, docname,
                            'reverse-' + revname, platforms, qualifier, synopsis])
            prev_revname = revname

        # apply heuristics when to collapse modindex at page load:
        # only collapse if number of toplevel reverses is larger than
        # number of submodules
        collapse = len(reverses) - num_toplevels < num_toplevels

        # sort by first letter
        content = sorted(content.iteritems())

        return content, collapse


class OperationHowto(Directive):
    """
    Directive to mark description of a new howto.
    """

    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        'platform': lambda x: x,
        'synopsis': lambda x: x,
        'reverse': lambda x: x,
        'noindex': directives.flag,
        'deprecated': directives.flag,
    }

    def run(self):
        env = self.state.document.settings.env
        howname = self.arguments[0].strip()
        noindex = 'noindex' in self.options
        env.temp_data['op:howto'] = howname
        ret = []
        if not noindex:
            env.domaindata['op']['howtos'][howname] = \
                (env.docname, self.options.get('synopsis', ''),
                 self.options.get('platform', ''), 'deprecated' in self.options)
            # make a duplicate entry in 'objects' to facilitate searching for
            # the howto in OperationDomain.find_obj()
            env.domaindata['op']['objects'][howname] = (env.docname, 'howto')
            targetnode = nodes.target('', '', ids=['howto-' + howname], ismod=True)
            self.state.document.note_explicit_target(targetnode)
            # the platform and synopsis aren't printed; in fact, they are only
            # used in the modindex currently
            ret.append(targetnode)
            indextext = _('%s (howto)') % howname
            inode = addnodes.index(entries=[('single', indextext, 'howto-' + howname, '')])
            ret.append(inode)

            ### 
            if 'reverse' in self.options:
                if self.options.get('platform', ''):
                    revname = '%s (%s)' % (self.options.get('reverse', ''), self.options.get('platform', ''))
                else:
                    revname = self.options.get('reverse', '')
                env.temp_data['op:reverse'] = revname
                env.domaindata['op']['reverses'][revname] = \
                    (env.docname, self.options.get('synopsis', ''),
                     None, 'deprecated' in self.options)
                env.domaindata['op']['objects'][revname] = (env.docname, 'reverse')
                targetnode = nodes.target('', '', ids=['reverse-' + revname],
                                          ismod=True)
                self.state.document.note_explicit_target(targetnode)
                ret.append(targetnode)
                indextext = _('%s (reverse)') % revname
                inode = addnodes.index(entries=[('single', indextext,
                                                 'reverse-' + revname, '')])
                ret.append(inode)

        return ret


class OperationHowtoIndex(Index):
    """
    Index subclass to provide the Operation howto index.
    """

    name = 'howtoindex'
    localname = l_('Howto Index')
    shortname = l_('Howto')

    def generate(self, docnames=None):
        content = {}
        # list of all howtos, sorted by howto name
        howtos = sorted(self.domain.data['howtos'].iteritems(),
                         key=lambda x: x[0].lower())
        # sort out collapsable howtos
        prev_howname = ''
        num_toplevels = 0
        for howname, (docname, synopsis, platforms, deprecated) in howtos:
            entries = content.setdefault(howname[0].lower(), [])

            package = howname.split('.')[0]
            if package != howname:
                # it's a subentries
                if prev_howname == package:
                    # first subentries - make parent a group head
                    if entries:
                        entries[-1][1] = 1
                elif not prev_howname.startswith(package):
                    # subentries without parent in list, add dummy entry
                    entries.append([package, 1, '', '', '', '', ''])
                subtype = 2
                entriename = howname.split(package + '.', 1)[1]
            else:
                num_toplevels += 1
                subtype = 0
                entriename = howname

            qualifier = deprecated and _('Deprecated') or ''
            entries.append([entriename, subtype, docname,
                            'howto-' + howname, platforms, qualifier, synopsis])
            prev_howname = howname

        # apply heuristics when to collapse modindex at page load:
        # only collapse if number of toplevel howtos is larger than
        # number of submodules
        collapse = len(howtos) - num_toplevels < num_toplevels

        # sort by first letter
        content = sorted(content.iteritems())

        return content, collapse

class OperationDomain(Domain):
    """Operation domain."""
    name = 'op'
    label = 'Operation'
    object_types = {
        'command':       ObjType(l_('command'),        'command'),
        'setting':       ObjType(l_('setting'),        'setting'),
        'install':       ObjType(l_('install'),        'install'),
        'howto':         ObjType(l_('howto'),           'howto'),
    }

    directives = {
        'command':         OperationCommand,
        'setting':         OperationSetting,
        'install':         OperationInstall,
        'howto':           OperationHowto,
    }
    roles = {
        'command':   OperationXRefRole(),
        'setting':   OperationXRefRole(),
        'install':   OperationXRefRole(),
        'howto':     OperationXRefRole(),
    }
    initial_data = {
        'objects': {},  # fullname -> docname, objtype
        'commands': {}, # comname -> comname, synopsis, platform, deprecated
        'settings': {}, # setname -> setname, synopsis, platform, deprecated
        'installs': {}, # insname -> insname, synopsis, platform, deprecated
        'reverses': {}, # revname -> revname, synopsis, platform, deprecated
        'howtos': {},   # howname -> howname, synopsis, platform, deprecated
    }
    indices = [
        OperationHowtoIndex,
        OperationCommandIndex,
        OperationSettingIndex,
        OperationInstallIndex,
        OperationReverseIndex,
    ]
    types = {
        'command': 'commands',
        'setting': 'settings',
        'install': 'installs',
        'reverse': 'reverses',
        'howto': 'howtos',
    }

    def clear_doc(self, docname):
        for fullname, (fn, _) in self.data['objects'].items():
            if fn == docname:
                del self.data['objects'][fullname]
        for comname, (fn, _, _, _) in self.data['commands'].items():
            if fn == docname:
                del self.data['commands'][comname]
        for setname, (fn, _, _, _) in self.data['settings'].items():
            if fn == docname:
                del self.data['settings'][setname]
        for insname, (fn, _, _, _) in self.data['installs'].items():
            if fn == docname:
                del self.data['installs'][insname]
        for revname, (fn, _, _, _) in self.data['reverses'].items():
            if fn == docname:
                del self.data['reverses'][revname]
        for howname, (fn, _, _, _) in self.data['howtos'].items():
            if fn == docname:
                del self.data['howtos'][howname]

    def find_obj(self, env, comname, setname, insname, revname, howname, name, type, searchmode=0):
        """Find a Operation object for "name", perhaps using the given command
           Returns a list of (name, object entry) tuples.
        """

        if not name:
            return []

        objects = self.data['objects']
        matches = []

        newname = None
        if searchmode == 1:
            objtypes = self.objtypes_for_role(type)
            if objtypes is not None:
                if not newname:
                    if comname and comname + '.' + name in objects and \
                       objects[comname + '.' + name][1] in objtypes:
                        newname = comname + '.' + name
                    elif setname and setname + '.' + name in objects and \
                       objects[setname + '.' + name][1] in objtypes:
                        newname = setname + '.' + name
                    elif insname and insname + '.' + name in objects and \
                       objects[insname + '.' + name][1] in objtypes:
                        newname = insname + '.' + name
                    elif revname and revname + '.' + name in objects and \
                       objects[revname + '.' + name][1] in objtypes:
                        newname = revname + '.' + name
                    elif howname and howname + '.' + name in objects and \
                       objects[howname + '.' + name][1] in objtypes:
                        newname = howname + '.' + name
                    elif name in objects and objects[name][1] in objtypes:
                        newname = name
                    else:
                        # "fuzzy" searching mode
                        searchname = '.' + name
                        matches = [(oname, objects[oname]) for oname in objects
                                   if oname.endswith(searchname)
                                   and objects[oname][1] in objtypes]
        else:
            # NOTE: searching for exact match, object type is not considered
            if name in objects:
                newname = name
            elif comname and comname + '.' + name in objects:
                newname = comname + '.' + name
            elif setname and setname + '.' + name in objects:
                newname = setname + '.' + name
            elif insname and insname + '.' + name in objects:
                newname = insname + '.' + name
            elif revname and revname + '.' + name in objects:
                newname = revname + '.' + name
            elif howname and howname + '.' + name in objects:
                newname = howname + '.' + name
        if newname is not None:
            matches.append((newname, objects[newname]))
        return matches

    def resolve_xref(self, env, fromdocname, builder, type, target, node, contnode):
        comname = node.get('op:command')
        setname = node.get('op:setting')
        insname = node.get('op:install')
        revname = node.get('op:reverse')
        howname = node.get('op:howto')
        searchmode = node.hasattr('refspecific') and 1 or 0
        matches = self.find_obj(env, comname, setname, insname, revname, howname, target, type, searchmode)

        if not matches:
            return None
        elif len(matches) > 1:
            env.warn_node(
                'more than one target found for cross-reference '
                '%r: %s' % (target, ', '.join(match[0] for match in matches)),
                node)
        name, obj = matches[0]

        if obj[1] == type:
            # get additional info for howtos
            docname, synopsis, platform, deprecated = self.data[self.types[type]][name]
            assert docname == obj[0]
            title = name
            if synopsis:
                title += ': ' + synopsis
            if deprecated:
                title += _(' (deprecated)')
            if platform:
                title += ' (' + platform + ')'
            return make_refnode(builder, fromdocname, docname, type + '-' + name, contnode, title)
        else:
            return make_refnode(builder, fromdocname, obj[0], name, contnode, name)

    def get_objects(self):
        for x, y in self.types.iteritems():
            for objname, info in self.data[y].iteritems():
                yield (objname, objname, x, info[0], x + '-' + objname, 0)
        for refname, (docname, type) in self.data['objects'].iteritems():
            yield (refname, refname, type, docname, refname, 1)

def setup(app):
    app.add_domain(OperationDomain)
