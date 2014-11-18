# -*- coding: utf-8 -*-
"""
    weppy.templating
    ----------------

    Provides the templating system for weppy.

    :copyright: (c) 2014 by Giovanni Barillari

    Based on the web2py's templating system (http://www.web2py.com)
    :copyright: (c) by Massimo Di Pierro <mdipierro@cs.depaul.edu>

    :license: BSD, see LICENSE for more details.
"""

import os
import cgi
from re import compile, sub, escape, DOTALL
from ._compat import StringIO


class TemplateError(Exception):
    def __init__(self, parser, message, filename, lineno):
        Exception.__init__(self, message)
        self.parser = parser
        self.template = filename
        if isinstance(lineno, tuple):
            lineno = lineno[0]
        self.lineno = lineno

    @property
    def file_path(self):
        return os.path.join(self.parser.path, self.template)


class TemplateReference(object):
    def __init__(self, parser, code, exc_type, exc_value, tb):
        self.parser = parser
        self.exc_type = exc_type
        self.exc_value = exc_value
        self.tb = tb
        if hasattr(exc_value, 'lineno'):
            dummy_lineno = exc_value.lineno
        else:
            import traceback
            template_frame = traceback.extract_tb(tb, 2)[-1]
            dummy_lineno = template_frame[1]
        self.lines = self.get_template_reference(parser.content,
                                                 parser.content.blocks)
        self.template, self.lineno = self.match_template(dummy_lineno)

    @property
    def file_path(self):
        return os.path.join(self.parser.path, self.template)

    @property
    def message(self):
        location = 'File "%s", line %d' % (self.file_path, self.lineno)
        lines = [self.args[0], '  ' + location]
        return "\n".join(lines)

    def __str__(self):
        #return self.message
        return str(self.exc_value)

    @staticmethod
    def get_template_reference(content, blocks):
        lines = []
        for node in content.nodes:
            if isinstance(node, BlockNode):
                if node.name in blocks:
                    lines += TemplateReference.get_template_reference(
                        blocks[node.name], blocks)
                else:
                    lines += TemplateReference.get_template_reference(node,
                                                                      blocks)
            else:
                node_lines = node._rendered_lines()
                if len(node_lines) == node.lines[1]-node.lines[0]+1:
                    linenos = [(i, i+1) for i in range(node.lines[0],
                                                       node.lines[1]+1)]
                else:
                    linenos = [(node.lines[0], node.lines[1])
                               for i in range(0, len(node_lines))]
                for l in range(0, len(node_lines)):
                    lines.append((node.template, linenos[l]))
        return lines

    def match_template(self, dummy_lineno):
        try:
            reference = self.lines[dummy_lineno-1]
        except:
            reference = (self.parser.name, ('<unknown>', 'unknown'))
        return reference[0], reference[1][0]


class Node(object):
    """
    Basic Container Object
    """
    def __init__(self, value=None, pre_extend=False, template=None,
                 lines=None):
        self.value = value
        self.pre_extend = pre_extend
        self.template = template
        self.lines = lines or (None, None)

    def __str__(self):
        return str(self.value)

    def _rendered_lines(self):
        return str(self.value).split("\n")[1:]


class SuperNode(Node):
    def __init__(self, name='', pre_extend=False):
        self.name = name
        self.value = None
        self.pre_extend = pre_extend

    def __str__(self):
        if self.value:
            return str(self.value)
        else:
            return ''

    def __repr__(self):
        return "%s->%s" % (self.name, self.value)


def output_aux(node, blocks):
    # If we have a block level
    #   If we can override this block.
    #     Override block from vars.
    #   Else we take the default
    # Else its just a string
    return (blocks[node.name].output(blocks)
            if node.name in blocks else
            node.output(blocks)) \
        if isinstance(node, BlockNode) \
        else str(node)


class BlockNode(Node):
    """
    Block Container.

    This Node can contain other Nodes and will render in a hierarchical order
    of when nodes were added.

    ie::

        {{ block test }}
            This is default block test
        {{ end }}
    """
    def __init__(self, name='', pre_extend=False, delimiters=('{{', '}}')):
        """
        name - Name of this Node.
        """
        self.nodes = []
        self.name = name
        self.pre_extend = pre_extend
        self.left, self.right = delimiters

    def __repr__(self):
        lines = ['%sblock %s%s' % (self.left, self.name, self.right)]
        lines += [str(node) for node in self.nodes]
        lines.append('%send%s' % (self.left, self.right))
        return ''.join(lines)

    def __str__(self):
        """
        Get this BlockNodes content, not including child Nodes
        """
        return ''.join(str(node) for node in self.nodes
                       if not isinstance(node, BlockNode))

    def append(self, node):
        """
        Add an element to the nodes.

        Keyword Arguments

        - node -- Node object or string to append.
        """
        if isinstance(node, (str, Node)):
            self.nodes.append(node)
        else:
            raise TypeError("Invalid type; must be instance of ``str`` or ``BlockNode``. %s" % node)

    def extend(self, other):
        """
        Extend the list of nodes with another BlockNode class.

        Keyword Arguments

        - other -- BlockNode or Content object to extend from.
        """
        if isinstance(other, BlockNode):
            self.nodes.extend(other.nodes)
        else:
            raise TypeError(
                "Invalid type; must be instance of ``BlockNode``. %s" % other)

    def output(self, blocks):
        """
        Merges all nodes into a single string.
        blocks -- Dictionary of blocks that are extending
        from this template.
        """
        return ''.join(output_aux(node, blocks) for node in self.nodes)


class Content(BlockNode):
    """
    Parent Container -- Used as the root level BlockNode.

    Contains functions that operate as such.
    """
    def __init__(self, name="ContentBlock", pre_extend=False):
        """
        Keyword Arguments

        name -- Unique name for this BlockNode
        """
        self.name = name
        self.nodes = []
        self.blocks = {}
        self.pre_extend = pre_extend
        self.template = name

    def __str__(self):
        return ''.join(output_aux(node, self.blocks) for node in self.nodes)

    def _insert(self, other, index=0):
        """
        Inserts object at index.
        """
        if isinstance(other, (str, Node)):
            self.nodes.insert(index, other)
        else:
            raise TypeError(
                "Invalid type, must be instance of ``str`` or ``Node``.")

    def insert(self, other, index=0):
        """
        Inserts object at index.

        You may pass a list of objects and have them inserted.
        """
        if isinstance(other, (list, tuple)):
            # Must reverse so the order stays the same.
            other.reverse()
            for item in other:
                self._insert(item, index)
        else:
            self._insert(other, index)

    def append(self, node):
        """
        Adds a node to list. If it is a BlockNode then we assign a block for it.
        """
        if isinstance(node, (str, Node)):
            self.nodes.append(node)
            if isinstance(node, BlockNode):
                self.blocks[node.name] = node
        else:
            raise TypeError("Invalid type, must be instance of ``str`` or ``BlockNode``. %s" % node)

    def extend(self, other):
        """
        Extends the objects list of nodes with another objects nodes
        """
        if isinstance(other, BlockNode):
            self.nodes.extend(other.nodes)
            self.blocks.update(other.blocks)
        else:
            raise TypeError(
                "Invalid type; must be instance of ``BlockNode``. %s" % other)

    def clear_content(self):
        self.nodes = []


class TemplateParser(object):

    default_delimiters = ('{{', '}}')
    r_tag = compile(r'(\{\{.*?\}\})', DOTALL)

    r_multiline = compile(r'(""".*?""")|(\'\'\'.*?\'\'\')', DOTALL)

    # These are used for re-indentation.
    # Indent + 1
    re_block = compile('^(elif |else:|except:|except |finally:).*$', DOTALL)

    # Indent - 1
    re_unblock = compile('^(return|continue|break|raise)( .*)?$', DOTALL)
    # Indent - 1
    re_pass = compile('^pass( .*)?$', DOTALL)

    def __init__(self, templater, text,
                 name="ParserContainer",
                 context=dict(),
                 path='views/',
                 writer='_DummyResponse_.write',
                 lexers={},
                 delimiters=('{{', '}}'),
                 _super_nodes = [],
                 ):
        """
        text -- text to parse
        context -- context to parse in
        path -- folder path to templates
        writer -- string of writer class to use
        lexers -- dict of custom lexers to use.
        delimiters -- for example ('{{','}}')
        _super_nodes -- a list of nodes to check for inclusion
                        this should only be set by "self.extend"
                        It contains a list of SuperNodes from a child
                        template that need to be handled.
        """
        self.templater = templater
        # Keep a root level name.
        self.name = name
        # Raw text to start parsing.
        self.text = text
        # Writer to use (refer to the default for an example).
        # This will end up as
        # "%s(%s, escape=False)" % (self.writer, value)
        self.writer = writer

        # Dictionary of custom name lexers to use.
        #if isinstance(lexers, dict):
        #    self.lexers = lexers
        #else:
        #    self.lexers = {}
        self.lexers = self.templater.lexers

        # Path of templates
        self.path = path
        # Context for templates.
        self.context = context

        # allow optional alternative delimiters
        self.delimiters = delimiters
        if delimiters != self.default_delimiters:
            escaped_delimiters = (escape(delimiters[0]),
                                  escape(delimiters[1]))
            self.r_tag = compile(r'(%s.*?%s)' % escaped_delimiters, DOTALL)
        #elif hasattr(context.get('response', None), 'delimiters'):
        #    if context['response'].delimiters != self.default_delimiters:
        #        escaped_delimiters = (
        #            escape(context['response'].delimiters[0]),
        #            escape(context['response'].delimiters[1]))
        #        self.r_tag = compile(r'(%s.*?%s)' % escaped_delimiters,
        #                             DOTALL)

        # Create a root level Content that everything will go into.
        self.content = Content(name=name)

        # Stack will hold our current stack of nodes.
        # As we descend into a node, it will be added to the stack
        # And when we leave, it will be removed from the stack.
        # self.content should stay on the stack at all times.
        self.stack = [self.content]

        # This variable will hold a reference to every super block
        # that we come across in this template.
        self.super_nodes = []

        # This variable will hold a reference to the child
        # super nodes that need handling.
        self.child_super_nodes = _super_nodes

        # This variable will hold a reference to every block
        # that we come across in this template
        self.blocks = {}

        self.current_lines = (1, 1)

        # Begin parsing.
        self.parse(text)

    def create_block(self, name=None, pre_extend=False, delimiters=None):
        return BlockNode(name=name, pre_extend=pre_extend,
                         delimiters=delimiters or self.delimiters)

    def create_node(self, value, pre_extend=False, use_writer=True,
                    writer_escape=True):
        if use_writer:
            if not writer_escape:
                value = "\n%s(%s, escape=False)" % (self.writer, value)
            else:
                value = "\n%s(%s)" % (self.writer, value)
        else:
            value = "\n%s" % value
        return Node(value, pre_extend=pre_extend, template=self.name,
                    lines=self.current_lines)

    def create_htmlnode(self, value, pre_extend=False):
        value = "\n%s(%r, escape=False)" % (self.writer, value)
        return Node(value, pre_extend=pre_extend, template=self.name,
                    lines=self.current_lines)

    def to_string(self):
        """
        Return the parsed template with correct indentation.

        Used to make it easier to port to python3.
        """
        return self.reindent(str(self.content))

    def __str__(self):
        "Make sure str works exactly the same as python 3"
        return self.to_string()

    def __unicode__(self):
        "Make sure str works exactly the same as python 3"
        return self.to_string()

    def reindent(self, text):
        """
        Reindents a string of unindented python code.
        """

        # Get each of our lines into an array.
        lines = text.split('\n')

        # Our new lines
        new_lines = []

        # Keeps track of how many indents we have.
        # Used for when we need to drop a level of indentation
        # only to reindent on the next line.
        credit = 0

        # Current indentation
        k = 0

        #################
        # THINGS TO KNOW
        #################

        # k += 1 means indent
        # k -= 1 means unindent
        # credit = 1 means unindent on the next line.

        for raw_line in lines:
            line = raw_line.strip()

            # ignore empty lines
            if not line:
                continue

            # If we have a line that contains python code that
            # should be unindented for this line of code.
            # and then reindented for the next line.
            if TemplateParser.re_block.match(line):
                k = k + credit - 1

            # We obviously can't have a negative indentation
            k = max(k, 0)

            # Add the indentation!
            new_lines.append(' ' * (4 * k) + line)

            # Bank account back to 0 again :(
            credit = 0

            # If we are a pass block, we obviously de-dent.
            if TemplateParser.re_pass.match(line):
                k -= 1

            # If we are any of the following, de-dent.
            # However, we should stay on the same level
            # But the line right after us will be de-dented.
            # So we add one credit to keep us at the level
            # while moving back one indentation level.
            if TemplateParser.re_unblock.match(line):
                credit = 1
                k -= 1

            # If we are an if statement, a try, or a semi-colon we
            # probably need to indent the next line.
            if line.endswith(':') and not line.startswith('#'):
                k += 1

        # This must come before so that we can raise an error with the
        # right content.
        new_text = '\n'.join(new_lines)

        if k > 0:
            #self._raise_error('missing "pass" in view', new_text)
            raise TemplateError(self, 'missing "pass" in view', self.name, 1)
        elif k < 0:
            #self._raise_error('too many "pass" in view', new_text)
            raise TemplateError(self, 'too many "pass" in view', self.name, 1)

        return new_text

    def _get_file_text(self, filename):
        """
        Attempt to open ``filename`` and retrieve its text.

        This will use self.path to search for the file.
        """

        # If they didn't specify a filename, how can we find one!
        if not filename.strip():
            #self._raise_error('Invalid template filename')
            raise TemplateError(self, 'Invalid template filename', self.name,
                                1)

        # Allow Views to include other views dynamically
        context = self.context
        #if current and not "response" in context:
        #    context["response"] = getattr(current, 'response', None)

        # Get the filename; filename looks like ``"template.html"``.
        # We need to eval to remove the quotes and get the string type.
        filename = eval(filename, context)

        # Get the path of the file on the system.
        #filepath = self.path and os.path.join(self.path, filename) or filename

        ## Get the file and read the content
        tpath, tname = self.templater.preload(
            self.path, filename)
        filepath = tpath and os.path.join(tpath, tname) or tname
        try:
            tsource = self.templater.load(filepath)
        except:
            raise TemplateError(self, 'Unable to open included view file',
                                self.name, 1)
        tsource = self.templater.prerender(tsource, filepath)

        return tsource, tname

    def include(self, content, filename):
        """
        Include ``filename`` here.
        """
        text, tname = self._get_file_text(filename)

        t = TemplateParser(self.templater, text,
                           name=tname,
                           context=self.context,
                           path=self.path,
                           writer=self.writer,
                           delimiters=self.delimiters)

        content.append(t.content)

    def extend(self, filename):
        """
        Extend ``filename``. Anything not declared in a block defined by the
        parent will be placed in the parent templates ``{{include}}`` block.
        """
        text, tname = self._get_file_text(filename)

        # Create out nodes list to send to the parent
        super_nodes = []
        # We want to include any non-handled nodes.
        super_nodes.extend(self.child_super_nodes)
        # And our nodes as well.
        super_nodes.extend(self.super_nodes)

        t = TemplateParser(self.templater, text,
                           name=tname,
                           context=self.context,
                           path=self.path,
                           writer=self.writer,
                           delimiters=self.delimiters,
                           _super_nodes=super_nodes)

        # Make a temporary buffer that is unique for parent
        # template.
        buf = BlockNode(
            name='__include__' + tname, delimiters=self.delimiters)
        pre = []

        # Iterate through each of our nodes
        for node in self.content.nodes:
            # If a node is a block
            if isinstance(node, BlockNode):
                # That happens to be in the parent template
                if node.name in t.content.blocks:
                    # Do not include it
                    continue

            if isinstance(node, Node):
                # Or if the node was before the extension
                # we should not include it
                if node.pre_extend:
                    pre.append(node)
                    continue

            # Otherwise, it should go int the
            # Parent templates {{include}} section.
                buf.append(node)
            else:
                buf.append(node)

        # Clear our current nodes. We will be replacing this with
        # the parent nodes.
        self.content.nodes = []

        t_content = t.content

        # Set our include, unique by filename
        t_content.blocks['__include__' + tname] = buf

        # Make sure our pre_extended nodes go first
        t_content.insert(pre)

        # Then we extend our blocks
        t_content.extend(self.content)

        # Work off the parent node.
        self.content = t_content

    def parse(self, text):

        # Basically, r_tag.split will split the text into
        # an array containing, 'non-tag', 'tag', 'non-tag', 'tag'
        # so if we alternate this variable, we know
        # what to look for. This is alternate to
        # line.startswith("{{")
        in_tag = False
        extend = None
        pre_extend = True

        # Use a list to store everything in
        # This is because later the code will "look ahead"
        # for missing strings or brackets.
        ij = self.r_tag.split(text)
        # j = current index
        # i = current item

        stack = self.stack
        for j in range(len(ij)):
            i = ij[j]

            if i:
                self.current_lines = (self.current_lines[1],
                                      self.current_lines[1] +
                                      len(i.split("\n"))-1)

                if not stack:
                    raise TemplateError(self,
                        'The "end" tag is unmatched, please check if you have a starting "block" tag',
                        self.name, self.current_lines)

                # Our current element in the stack.
                top = stack[-1]

                if in_tag:
                    line = i

                    # Get rid of '{{' and '}}'
                    line = line[2:-2].strip()

                    # This is bad juju, but let's do it anyway
                    if not line:
                        continue

                    # We do not want to replace the newlines in code,
                    # only in block comments.
                    def remove_newline(re_val):
                        # Take the entire match and replace newlines with
                        # escaped newlines.
                        return re_val.group(0).replace('\n', '\\n')

                    # Perform block comment escaping.
                    # This performs escaping ON anything
                    # in between """ and """
                    line = sub(TemplateParser.r_multiline,
                               remove_newline,
                               line)

                    if line.startswith('='):
                        # IE: {{=response.title}}
                        name, value = '=', line[1:].strip()
                    else:
                        v = line.split(' ', 1)
                        if len(v) == 1:
                            # Example
                            # {{ include }}
                            # {{ end }}
                            name = v[0]
                            value = ''
                        else:
                            # Example
                            # {{ block pie }}
                            # {{ include "layout.html" }}
                            # {{ for i in range(10): }}
                            name = v[0]
                            value = v[1]

                    # This will replace newlines in block comments
                    # with the newline character. This is so that they
                    # retain their formatting, but squish down to one
                    # line in the rendered template.

                    # First check if we have any custom lexers
                    if name in self.lexers:
                        # Pass the information to the lexer
                        # and allow it to inject in the environment

                        # You can define custom names such as
                        # '{{<<variable}}' which could potentially
                        # write unescaped version of the variable.
                        evalue = eval(value, self.context) if value else None
                        self.lexers[name](parser=self,
                                          value=evalue,
                                          top=top,
                                          stack=stack)

                    elif name == '=':
                        # So we have a variable to insert into
                        # the template
                        node = self.create_node(value, pre_extend)
                        top.append(node)

                    elif name == 'block' and not value.startswith('='):
                        # Make a new node with name.
                        node = self.create_block(value.strip(), pre_extend)

                        # Append this node to our active node
                        top.append(node)

                        # Make sure to add the node to the stack.
                        # so anything after this gets added
                        # to this node. This allows us to
                        # "nest" nodes.
                        stack.append(node)

                    elif name == 'end' and not value.startswith('='):
                        # We are done with this node.

                        # Save an instance of it
                        self.blocks[top.name] = top

                        # Pop it.
                        stack.pop()

                    elif name == 'super' and not value.startswith('='):
                        # Get our correct target name
                        # If they just called {{super}} without a name
                        # attempt to assume the top blocks name.
                        if value:
                            target_node = value
                        else:
                            target_node = top.name

                        # Create a SuperNode instance
                        node = SuperNode(name=target_node,
                                         pre_extend=pre_extend)

                        # Add this to our list to be taken care of
                        self.super_nodes.append(node)

                        # And put in in the tree
                        top.append(node)

                    elif name == 'include' and not value.startswith('='):
                        # If we know the target file to include
                        if value:
                            self.include(top, value)

                        # Otherwise, make a temporary include node
                        # That the child node will know to hook into.
                        else:
                            include_node = BlockNode(
                                name='__include__' + self.name,
                                pre_extend=pre_extend,
                                delimiters=self.delimiters)
                            top.append(include_node)

                    elif name == 'include_helpers' and \
                            not value.startswith('='):
                        helpers = [
                            '<script type="text/javascript" src="/__weppy__/jquery.min.js"></script>',
                            '<script type="text/javascript" src="/__weppy__/helpers.js"></script>']
                        node = self.create_htmlnode(
                            "\n".join(h for h in helpers), pre_extend)
                        top.append(node)

                    elif name == 'include_meta' and not value.startswith('='):
                        if not value:
                            value = 'current.response.get_meta()'
                        node = self.create_node(value, pre_extend,
                                                writer_escape=False)
                        top.append(node)

                    elif name == 'include_static' and not \
                            value.startswith('='):
                        url = eval(value, self.context)
                        file_name = url.split("?")[0]
                        from .expose import url as murl
                        url = murl('static', file_name)
                        file_ext = file_name.rsplit(".", 1)[-1]
                        if file_ext == 'js':
                            static = '<script type="text/javascript" src="'+url+'"></script>'
                        elif file_ext == "css":
                            static = '<link rel="stylesheet" href="'+url+'" type="text/css" />'
                        else:
                            static = None
                        if static:
                            node = self.create_htmlnode(static, pre_extend)
                            top.append(node)

                    elif name == 'extend' and not value.startswith('='):
                        # We need to extend the following
                        # template.
                        extend = value
                        pre_extend = False

                    else:
                        # If we don't know where it belongs
                        # we just add it anyways without formatting.
                        if line and in_tag:

                            # Split on the newlines >.<
                            tokens = line.split('\n')

                            # We need to look for any instances of
                            # for i in range(10):
                            #   = i
                            # pass
                            # So we can properly put a response.write() in place.
                            continuation = False
                            len_parsed = 0
                            for k, token in enumerate(tokens):

                                token = tokens[k] = token.strip()
                                len_parsed += len(token)

                                if token.startswith('='):
                                    if token.endswith('\\'):
                                        continuation = True
                                        tokens[k] = "%s(%s" % (
                                            self.writer, token[1:].strip())
                                    else:
                                        tokens[k] = "%s(%s)" % (
                                            self.writer, token[1:].strip())
                                elif continuation:
                                    tokens[k] += ')'
                                    continuation = False

                            buf = '\n'.join(tokens)
                            node = self.create_node(buf, pre_extend,
                                                    use_writer=False)
                            top.append(node)

                else:
                    # It is HTML so just include it.
                    node = self.create_htmlnode(i, pre_extend)
                    top.append(node)

            # Remember: tag, not tag, tag, not tag
            in_tag = not in_tag

        # Make a list of items to remove from child
        to_rm = []

        # Go through each of the children nodes
        for node in self.child_super_nodes:
            # If we declared a block that this node wants to include
            if node.name in self.blocks:
                # Go ahead and include it!
                node.value = self.blocks[node.name]
                # Since we processed this child, we don't need to
                # pass it along to the parent
                to_rm.append(node)

        # Remove some of the processed nodes
        for node in to_rm:
            # Since this is a pointer, it works beautifully.
            # Sometimes I miss C-Style pointers... I want my asterisk...
            self.child_super_nodes.remove(node)

        # If we need to extend a template.
        if extend:
            self.extend(extend)


class DummyResponse():
    def __init__(self):
        self.body = StringIO()

    #def write(self, data, escape=True):
    #    if not escape:
    #        self.body.write(str(data))
    #    elif hasattr(data, 'xml') and callable(data.xml):
    #        self.body.write(data.xml())
    #    else:
    #        # make it a string
    #        if not isinstance(data, (str, unicode)):
    #            data = str(data)
    #        elif isinstance(data, unicode):
    #            data = data.encode('utf8', 'xmlcharrefreplace')
    #        data = cgi.escape(data, True).replace("'", "&#x27;")
    #        self.body.write(data)
    def write(self, data, escape=True):
        body = None
        if not escape:
            body = str(data)
        else:
            if hasattr(data, 'xml') and callable(data.xml):
                try:
                    body = data.xml()
                except:
                    pass
        if body is None:
            # make it a string
            if not isinstance(data, (str, unicode)):
                data = str(data)
            elif isinstance(data, unicode):
                data = data.encode('utf8', 'xmlcharrefreplace')
            body = cgi.escape(data, True).replace("'", "&#x27;")
        self.body.write(body)


class NOESCAPE():
    """
    A little helper to avoid escaping.
    """
    def __init__(self, text):
        self.text = text

    def xml(self):
        return self.text


class Templater(object):
    def __init__(self, application):
        self.loaders = application.template_preloaders
        self.renders = application.template_extensions
        self.lexers = application.template_lexers

    def preload(self, path, name):
        fext = os.path.splitext(name)[1]
        return reduce(lambda s, e: e.preload(s[0], s[1]),
                      self.loaders.get(fext, []), (path, name))

    def load(self, filename):
        try:
            file_obj = open(filename, 'rb')
            source = file_obj.read()
            file_obj.close()
        except IOError:
            raise RuntimeError('Unable to open template file: ' + filename)
        return source

    def prerender(self, source, filename):
        return reduce(lambda s, e: e.preprocess(s, filename),
                      self.renders, str(source))

    def render(self, source='', path=None, filename=None, context={}):
        if not 'asis' in context:
            from .tags import asis
            context['asis'] = asis
        if not 'load_component' in context:
            from .helpers import load_component
            context['load_component'] = load_component
        context['_DummyResponse_'] = DummyResponse()
        parser = None
        code = None
        try:
            parser = TemplateParser(self, source, name=filename,
                                    context=context, path=path)
            code = str(parser)
            exec(code) in context
        except:
            import sys
            exc_info = sys.exc_info()
            try:
                template_ref = TemplateReference(parser, code, exc_info[0],
                                                 exc_info[1], exc_info[2])
            except:
                template_ref = None
            context['__weppy_template__'] = template_ref
            from .debug import make_traceback
            make_traceback(exc_info, template_ref)
        return context['_DummyResponse_'].body.getvalue()


def render_template(application, filename):
    templater = Templater(application)
    tpath, tname = templater.preload(application.template_path, filename)
    filepath = os.path.join(tpath, tname)
    tsource = templater.load(filepath)
    tsource = templater.prerender(tsource, tname)
    from .globals import current
    from .expose import url
    context = dict(current=current, url=url)
    return templater.render(tsource, tpath, tname, context)


def render(application, path, template, context):
    templater = Templater(application)
    tpath, tname = templater.preload(path, template)
    filepath = os.path.join(tpath, tname)
    if not os.path.exists(filepath):
        from .http import HTTP
        raise HTTP(404, body="Invalid view\n")
    tsource = templater.load(filepath)
    tsource = templater.prerender(tsource, tname)
    return templater.render(tsource, tpath, tname, context.copy())
