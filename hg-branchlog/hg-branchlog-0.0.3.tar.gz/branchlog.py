# coding=utf-8
#
# Compact revision graph generator for Mercurial
#
# A modified version of mercurial's own graphlog. Copyright notices for the
# original files are included below. The modifications are
#   Copyright 2014 Tikitu de Jager <tikitu@logophile.org>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

import mercurial
from mercurial import cmdutil, commands, scmutil, templatekw, graphmod
from mercurial.cmdutil import getgraphlogrevs, show_changeset
from mercurial.graphmod import _fixlongrightedges
import mercurial.dagutil
import mercurial.node
from mercurial.i18n import _

testedwith = '2.9'
__version__ = '0.0.3'


class CompactDAG(mercurial.dagutil.genericdag):

    def __init__(self, forward, backward,
                 skip_d,
                 skip_counts,
                 suppressed,
                 forward_parents,
                 backward_parents,
                 interesting):
        super(CompactDAG, self).__init__()
        self.forward = forward
        self.backward = backward
        self.skip_d = skip_d
        self.skip_counts = skip_counts
        self.suppressed = suppressed
        self.forward_parents = forward_parents
        self.backward_parents = backward_parents
        self._interesting = interesting

    def _internalize(self, idx):
        return self.forward._internalize(idx)

    def _internalizeall(self, idxs):
        return self.forward._internalizeall(idxs)

    def _externalize(self, ix):
        return self.forward._externalize(ix)

    def _externalizeall(self, ixs):
        return self.forward.externalizeall(ixs)

    def nodeset(self):
        return set(self.skip_d.keys())

    def heads(self):
        return self.forward.heads()

    def parents(self, ix):
        return self.forward_parents.get(self.skip_d[ix], [])

    def inverse(self):
        return CompactDAG(forward=self.backward,
                          backward=self.forward,
                          skip_d=self.skip_d,
                          skip_counts=self.skip_counts,
                          forward_parents=self.backward_parents,
                          backward_parents=self.forward_parents,
                          interesting=self._interesting)

    def compacted(self, ix):
        return self.skip_d.get(ix)

    def interesting(self, ix):
        return ix in self._interesting and ix not in self.suppressed


def compactify(dag, repo=None, revs=set(), hide_close_branches=True):
    revs = set(revs)
    forward = dag
    backward = dag.inverse()

    skip_d = {}
    skip_counts = {}
    suppressed = set()

    interesting = set()
    boring = set()

    for ix in forward.nodeset():
        if ix not in revs:  # we don't care
            continue
        if ix in boring or ix in interesting:  # we've already seen it
            continue
        if hide_close_branches and repo[ix].closesbranch():
            revs.remove(ix)
            continue

        equivalent = set()
        agenda = [ix]
        while agenda:
            sub_ix = agenda.pop()
            if sub_ix not in revs:  # we don't care
                continue
            if hide_close_branches and repo[sub_ix].closesbranch():
                revs.remove(sub_ix)
                continue
            if sub_ix in equivalent or sub_ix in interesting:  # seen already
                continue

            # ix is interesting if it has tags
            ctx = repo[sub_ix]
            if ctx.tags():
                interesting.add(sub_ix)
                continue

            # ix is interesting if it's a root or a head
            forward_parents = forward.parents(sub_ix)
            backward_parents = backward.parents(sub_ix)
            if not forward_parents or not backward_parents:
                interesting.add(sub_ix)
                continue

            # ix is interesting if it has a parent on another branch
            branch = ctx.branch()
            if any(parent for parent in forward_parents
                   if repo[parent].branch() != branch):
                interesting.add(sub_ix)
                continue

            # ix is actually boring but we want to give it a DAG node anyway
            # if it is otherwise boring but has a child on another branch
            if any(child for child in backward_parents
                   if repo[child].branch() != branch):
                interesting.add(sub_ix)
                suppressed.add(sub_ix)
                continue

            # otherwise ix isn't interesting
            equivalent.add(sub_ix)
            agenda.extend(forward_parents)
            agenda.extend(backward_parents)

        boring.update(equivalent)
        for skip in equivalent:
            skip_d[skip] = ix
        skip_counts[ix] = len(equivalent)

    for ix in interesting:
        skip_d[ix] = ix
        skip_counts[ix] = 1

    forward_parents = {}
    backward_parents = {}
    for ix in interesting:
        forward_parents.setdefault(ix, []).extend(skip_d[parent] for parent in forward.parents(ix) if parent in revs)
        for child in backward.parents(ix):
            if child in revs:
                forward_parents.setdefault(skip_d[child], []).append(ix)
        backward_parents.setdefault(ix, []).extend(skip_d[parent] for parent in backward.parents(ix) if parent in revs)
        for child in forward.parents(ix):
            if child in revs:
                backward_parents.setdefault(skip_d[child], []).append(ix)

    for k in forward_parents:
        forward_parents[k] = sorted(set(forward_parents[k]))

    return CompactDAG(forward=forward, backward=backward,
                      skip_d=skip_d,
                      skip_counts=skip_counts,
                      suppressed=suppressed,
                      forward_parents=forward_parents,
                      backward_parents=backward_parents,
                      interesting=interesting)

# Original: hgext.graphlog
# ASCII graph log extension for Mercurial
# Copyright 2007 Joel Rosdahl <joel@rosdahl.net>

cmdtable = {}
command = cmdutil.command(cmdtable)


@command('branchlog',
    [('f', 'follow', None,
     _('follow changeset history, or file history across copies and renames')),
    ('', 'follow-first', None,
     _('only follow the first parent of merge changesets (DEPRECATED)')),
    ('d', 'date', '', _('show revisions matching date spec'), _('DATE')),
    ('C', 'copies', None, _('show copied files')),
    ('k', 'keyword', [],
     _('do case-insensitive search for a given text'), _('TEXT')),
    ('r', 'rev', [], _('show the specified revision or revset'), _('REV')),
    ('', 'removed', None, _('include revisions where files were removed')),
    ('m', 'only-merges', None, _('show only merges (DEPRECATED)')),
    ('u', 'user', [], _('revisions committed by user'), _('USER')),
    ('', 'only-branch', [],
     _('show only changesets within the given named branch (DEPRECATED)'),
     _('BRANCH')),
    ('b', 'branch', [],
     _('show changesets within the given named branch'), _('BRANCH')),
    ('P', 'prune', [],
     _('do not display revision or any of its ancestors'), _('REV')),
    ] + commands.logopts + commands.walkopts,
    _('[OPTION]... [FILE]'))
def branchlog(ui, repo, *pats, **opts):
    """show highlights of revision history alongside an ASCII revision graph

    Print a revision history alongside a revision graph drawn with
    ASCII characters, showing only "interesting" changesets. (What counts
    as interesting is still under revision.)

    Nodes printed as an @ character are parents of the working
    directory.
    """
    return branchlog_cmd(ui, repo, *pats, **opts)

# Original: mercurial.cmdutil
# cmdutil.py - help for command processing in mercurial
# Copyright 2005-2007 Matt Mackall <mpm@selenic.com>


def branchlog_cmd(ui, repo, *pats, **opts):
    # Parameters are identical to log command ones
    revs, expr, filematcher = getgraphlogrevs(repo, pats, opts)
    revdag = dagwalker(repo, revs)

    getrenamed = None
    if opts.get('copies'):
        endrev = None
        if opts.get('rev'):
            endrev = scmutil.revrange(repo, opts.get('rev')).max() + 1
        getrenamed = templatekw.getrenamedfn(repo, endrev=endrev)
    displayer = show_changeset(ui, repo, opts, buffered=True)
    showparents = [ctx.node() for ctx in repo[None].parents()]
    displaygraph(ui, revdag, displayer, showparents,
                 graphmod.asciiedges, getrenamed, filematcher)


def displaygraph(ui, dag, displayer, showparents, edgefn, getrenamed=None,
                 filematcher=None):
    seen, state = [], graphmod.asciistate()
    for rev, type_, ctx, parents, skipped_count in dag:
        char = 'o'
        if type_ == SKIPPED:
            char = u':'
        elif ctx.node() in showparents:
            char = '@'
        elif ctx.obsolete():
            char = 'x'
        copies = None
        if getrenamed and ctx.rev():
            copies = []
            for fn in ctx.files():
                rename = getrenamed(fn, ctx.rev())
                if rename:
                    copies.append((fn, rename[0]))
        revmatchfn = None
        if filematcher is not None:
            revmatchfn = filematcher(ctx.rev())
        displayer.show(ctx, copies=copies, matchfn=revmatchfn)
        if type_ == CHANGESET:
            lines = displayer.hunk.pop(rev).split('\n')
        elif type_ == SKIPPED:
            displayer.hunk.pop(rev)
            lines = ['({} changeset{} {})'.format(
                skipped_count,
                's e.g.' if skipped_count != 1 else ':',
                rev)]
        if not lines[-1]:
            del lines[-1]
        displayer.flush(rev)
        edges = edgefn(type_, char, lines, seen, rev, parents)
        for type_, char, lines, coldata in edges:
            ascii(ui, state, type_, char, lines, coldata)
    displayer.close()

# Original: mercurial.graphmod
# Revision graph generator for Mercurial
# Copyright 2008 Dirkjan Ochtman <dirkjan@ochtman.nl>
# Copyright 2007 Joel Rosdahl <joel@rosdahl.net>

CHANGESET = 'C'
SKIPPED = 's'


def dagwalker(repo, revs):
    """cset DAG generator yielding (id, CHANGESET, ctx, [parentids]) tuples

    This generator function walks through revisions (which should be ordered
    from bigger to lower). It returns a tuple for each node. The node and parent
    ids are arbitrary integers which identify a node in the context of the graph
    returned.
    """
    if not revs:
        return
    orig_revs = revs

    dag = compactify(mercurial.dagutil.revlogdag(repo.changelog), repo=repo,
                     revs=revs)
    revs = sorted(filter(None, set(dag.compacted(rev) for rev in revs)), reverse=True)

    get_ancestors = graphmod.grandparent

    changelog = repo.changelog
    lowest_rev = min(revs)
    ancestor_cache = {}

    for rev in revs:
        ctx = repo[rev]
        parents = sorted(set([dag.compacted(p.rev()) for p in ctx.parents()
                              if dag.compacted(p.rev()) in revs]))
        missing_parents = [p.rev() for p in ctx.parents() if
                 p.rev() != mercurial.node.nullrev and p.rev() not in parents and dag.compacted(p.rev()) not in parents]

        for missing_parent in missing_parents:
            ancestors = ancestor_cache.get(missing_parent)
            if ancestors is None:
                ancestors = ancestor_cache[missing_parent] = get_ancestors(changelog, lowest_rev, orig_revs, missing_parent)
            if not ancestors:
                parents.append(missing_parent)
            else:
                parents.extend(dag.compacted(g) for g in ancestors if dag.compacted(g) not in parents)
        parents = sorted(set(parents))

        if dag.interesting(rev):
            yield (ctx.rev(), graphmod.CHANGESET, ctx, parents, None)
        else:
            yield (ctx.rev(), SKIPPED, ctx, parents, dag.skip_counts[rev])


def _getnodelineedgestail(
        node_index, p_node_index, n_columns, n_columns_diff, p_diff, fix_tail):
    if fix_tail and n_columns_diff == p_diff and n_columns_diff != 0:
        # Still going in the same non-vertical direction.
        if n_columns_diff == -1:
            start = max(node_index + 1, p_node_index)
            tail = ["|", " ", ' '] * (start - node_index - 1)
            tail.extend(["/", " ", ' '] * (n_columns - start))
            return tail
        else:
            return ["\\", " ", ' '] * (n_columns - node_index - 1)
    else:
        return ["|", " ", ' '] * (n_columns - node_index - 1)


def _drawedges(edges, nodeline, interline):
    needs_extra_interline = False
    for (start, end) in edges:
        if start == end + 1:
            interline[3 * end + 2] = "/"
            needs_extra_interline = True
        elif start == end - 1:
            interline[3 * start + 1] = "\\"
            needs_extra_interline = True
        elif start == end:
            interline[3 * start] = "|"
        else:
            if 3 * end >= len(nodeline):
                continue
            nodeline[3 * end] = "|"
            step = 1 if start < end else -1
            for i in range(3 * start + step, 3 * end - step, step):
                if nodeline[i] == ' ':
                    nodeline[i] = "-"
    return needs_extra_interline


def _getpaddingline(ni, n_columns, edges):
    line = []
    line.extend(["|", " ", ' '] * ni)
    if (ni, ni - 1) in edges or (ni, ni) in edges:
        # (ni, ni - 1)      (ni, ni)
        # | | | |           | | | |
        # +---o |           | o---+
        # | | c |           | c | |
        # | |/ /            | |/ /
        # | | |             | | |
        c = "|"
    else:
        c = " "
    line.extend([c, " ", ' '])
    line.extend(["|", " ", ' '] * (n_columns - ni - 1))
    return line


def _shift(shift_interline):
    for (a, b, c) in zip(shift_interline[::3],
                         shift_interline[1::3],
                         shift_interline[2::3]):
        yield '|' if a == '|' else ' '
        yield '/' if c == '/' else ' '
        yield '\\' if b == '\\' else ' '


def ascii(ui, state, type, char, text, coldata):
    """prints an ASCII graph of the DAG

    takes the following arguments (one call per node in the graph):

      - ui to write to
      - Somewhere to keep the needed state in (init to asciistate())
      - Column of the current node in the set of ongoing edges.
      - Type indicator of node data, usually 'C' for changesets.
      - Payload: (char, lines):
        - Character to use as node's symbol.
        - List of lines to display as the node's text.
      - Edges; a list of (col, next_col) indicating the edges between
        the current node and its parents.
      - Number of columns (ongoing edges) in the current revision.
      - The difference between the number of columns (ongoing edges)
        in the next revision and the number of columns (ongoing edges)
        in the current revision. That is: -1 means one column removed;
        0 means no columns added or removed; 1 means one column added.
    """

    idx, edges, ncols, coldiff = coldata
    assert -2 < coldiff < 2
    if coldiff == -1 and False:  # wide columns mean we can happily cross
        # Transform
        #
        #     | | |        | | |
        #     o | |  into  o---+
        #     |X /         |/ /
        #     | |          | |
        _fixlongrightedges(edges)

    # add_padding_line says whether to rewrite
    #
    #     | | | |        | | | |
    #     | o---+  into  | o---+
    #     |  / /         |   | |  # <--- padding line
    #     o | |          |  / /
    #                    o | |
    add_padding_line = (len(text) > 2 and coldiff == -1 and
                        [x for (x, y) in edges if x + 1 < y])

    # fix_nodeline_tail says whether to rewrite
    #
    #     | | o | |        | | o | |
    #     | | |/ /         | | |/ /
    #     | o | |    into  | o / /   # <--- fixed nodeline tail
    #     | |/ /           | |/ /
    #     o | |            o | |
    fix_nodeline_tail = len(text) <= 2 and not add_padding_line

    # nodeline is the line containing the node character (typically o)
    nodeline = ["|", " ", ' '] * idx
    nodeline.extend([char, " ", ' '])

    nodeline.extend(
        _getnodelineedgestail(idx, state[1], ncols, coldiff,
                              state[0], fix_nodeline_tail))

    # shift_interlines are the lines containing the non-vertical
    # edges between this entry and the next
    shift_interline = ["|", " ", ' '] * idx
    if coldiff == -1:
        n_spaces = 1
        edge_ch = "/"
    elif coldiff == 0:
        n_spaces = 2
        edge_ch = "|"
    else:
        n_spaces = 3
        edge_ch = "\\"
    shift_interline.extend((n_spaces + 1) * [" "])
    shift_interline.extend([edge_ch, " ", ' '] * (ncols - idx - 1))
    needs_extra_interline = edge_ch in '/\\' and (ncols - idx - 1)

    # draw edges from the current node to its parents
    needs_extra_interline = _drawedges(edges, nodeline, shift_interline) or needs_extra_interline

    # lines is the list of all graph lines to print
    lines = [nodeline]
    if add_padding_line:
        lines.append(_getpaddingline(idx, ncols, edges))
    lines.append(shift_interline)
    if needs_extra_interline:
        lines.append(list(_shift(shift_interline)))
    for (start, end) in edges:
        if abs(start - end) > 1:
            step = 1 if start < end else -1
            shift_interline[3 * end - step] = '\\' if step > 0 else '/'
            if needs_extra_interline:
                lines[-1][3 * end] = '|'


    # make sure that there are as many graph lines as there are
    # log strings
    while len(text) < len(lines):
        text.append("")
    if len(lines) < len(text):
        extra_interline = ["|", " ", ' '] * (ncols + coldiff)
        while len(lines) < len(text):
            lines.append(extra_interline)

    # print lines
    indentation_level = max(ncols, ncols + coldiff)
    for (line, logstr) in zip(lines, text):
        ln = "%-*s %s" % (2 * indentation_level, "".join(line), logstr)
        ui.write(ln.rstrip() + '\n')

    # ... and start over
    state[0] = coldiff
    state[1] = idx
