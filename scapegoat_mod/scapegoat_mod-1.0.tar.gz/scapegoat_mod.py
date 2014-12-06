#!/usr/local/cpython-3.3/bin/python



# pylint: disable=superfluous-parens

'''
Provides a ScapeGoatTree class, parameterized by alpha

A high alpha value results in fewer balances, making insertion quicker
but lookups and deletions slower, and vice versa for a low alpha.
Therefore in practical applications, an alpha can be chosen depending on
how frequently these actions should be performed.
'''

import math

UNSPECIFIED = object()

def pad_to(string, length):
    '''Pad a string to a specified length'''
    return string + '_' * (length - len(string) - 1) + ' '

def center(string, field_use_width, field_avail_width):
    '''Center a string within a given field width'''
    field_use = (string + '_' * (field_use_width - 1))[:field_use_width - 1]
    pad_width = (field_avail_width - len(field_use)) / 2.0
    result = ' ' * int(pad_width) + field_use + ' ' * int(math.ceil(pad_width))
    return result

def printfn(key, value):
    '''print key, value pairs - used as a default visitation function for the traversal methods'''
    print('%s: %s' % (key, value))

class State(object):
    # pylint: disable=R0903
    # R0903: We don't need a lot of public methods
    '''A state class, used for iterating over the nodes in a scapegoat tree nonrecursively'''
    def __init__(self, todo, node):
        self.todo = todo
        self.node = node

    def __repr__(self):
        return '%s %s' % (self.todo, self.node)

class Node(object):
    # pylint: disable=too-few-public-methods

    '''One node of a scapegoat tree'''

    __slots__ = ('key', 'value', 'left', 'right')

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None

    def __repr__(self):
        return str('%s %s' % (self.key, self.value))

    __str__ = __repr__


class ScapeGoatTree(object):
    # pylint: disable=abstract-class-not-used

    '''Provides a ScapeGoatTree class'''

    def __init__(self, alpha):
        if not 0.5 < alpha < 1.0:
            raise ValueError('alpha not between 0.5 and 1.0 exclusive')
        self.alpha = alpha
        self.size = 0
        self.max_size = 0
        self.root = None

    # Return the number of keys on the subtree rooted by node (including node's key)
    def _size_of(self, node):
        '''Return the size of the tree'''
        if node is None:
            return 0
        return 1 + self._size_of(node.left) + self._size_of(node.right)

    def __len__(self):
        return self._size_of(self.root)

    def _hat(self):
        '''fundamental alpha-related calculation'''
        alpha_reciprocal = 1.0 / self.alpha
        log = math.log(self.size, alpha_reciprocal)
        return math.floor(log)

    def _is_deep(self, depth):
        '''Determine if a specific depth of a node makes the tree "deep"'''
        return depth > self._hat()

    @staticmethod
    def _get_brother_of(node, parent):
        '''Returns the brother node of "node", whose parent is "parent"'''
        if parent.left is not None and parent.left.key == node.key:
            return parent.right
        return parent.left

    @staticmethod
    def _rebuild_tree(root, length):
        '''Builds a new binary tree based on an old one. The new tree is balanced'''
        def flatten(node, nodes):
            '''Turn a binary tree into a list of nodes in sorted order'''
            if node is None:
                return
            flatten(node.left, nodes)
            nodes.append(node)
            flatten(node.right, nodes)

        def build_tree_from_sorted_list(nodes, start, end):
            '''Build a balanced binary tree from a sorted list of nodes'''
            if start > end:
                return None
            mid = int(math.ceil(start + (end - start) / 2.0))
            node = Node(nodes[mid].key, nodes[mid].value)
            node.left = build_tree_from_sorted_list(nodes, start, mid - 1)
            node.right = build_tree_from_sorted_list(nodes, mid + 1, end)
            return node

        nodes = []
        flatten(root, nodes)
        return build_tree_from_sorted_list(nodes, 0, length - 1)

    @staticmethod
    def _get_minimum(node):
        '''Returns the node with the minimum key in the subtree rooted by node'''
        while node.left is not None:
            node = node.left
        return node

    def find_min(self):
        '''Returns the minimum key in self'''
        node = self.root
        while node.left is not None:
            node = node.left
        return node.key

    def find_max(self):
        '''Returns the maximum key in self'''
        node = self.root
        while node.right is not None:
            node = node.right
        return node.key

    def __delitem__(self, key):
        # pylint: disable=too-many-branches

        '''Delete the key-value pair in the tree with a value of key'''

        node = self.root
        parent = None
        is_left_child = True
        # find the node, keep track of the parent, and side of the tree
        while node.key != key:
            parent = node
            if key > node.key:
                node = node.right
                is_left_child = False
            else:
                node = node.left
                is_left_child = True

        successor = None
        # case 1: Node to be delete has no children
        if node.left is None and node.right is None:
            pass
        # case 2: Node has only a right child
        elif node.left is None:
            successor = node.right
        # case 3: Node has only a left child
        elif node.right is None:
            successor = node.left
        # case 4: Node has right and left child
        else:
            # find successor
            successor = self._get_minimum(node.right)
            # the successor is the node's right child -- easy fix
            if successor == node.right:
                successor.left = node.left
            # complicated case
            else:
                print("finding successor")
                successor.left = node.left
                tmp = successor.right
                successor.right = node.right
                node.right.left = tmp

        # Replace the node
        if parent is None:
            self.root = successor
        elif is_left_child:
            parent.left = successor
        else:
            parent.right = successor

        self.size -= 1
        if self.size < self.alpha * self.max_size:
            #print "Rebuilding the whole tree"
            self.root = self._rebuild_tree(self.root, self.size)
            self.max_size = self.size

    def __getitem__(self, key):
        '''Look up the value at key'''
        node = self.root
        while node is not None:
            if node.key > key:
                node = node.left
            elif node.key < key:
                node = node.right
            else:
                return node.value

        raise KeyError

    def __setitem__(self, key, value):
        '''Added a key-value pair to the "dictionary"'''
        node_to_add = Node(key, value)
        yvar = None
        subtree = self.root
        # keep track of the depth and parents (so we don't have to recalculate
        # them)
        depth = 0
        parents = []
        # find where to place the node
        while subtree is not None:
            parents.insert(0, subtree)
            yvar = subtree
            if node_to_add.key < subtree.key:
                subtree = subtree.left
            else:
                subtree = subtree.right
            depth += 1

        if yvar is None:
            self.root = node_to_add
        elif node_to_add.key < yvar.key:
            yvar.left = node_to_add
        else:
            yvar.right = node_to_add

        self.size += 1
        self.max_size = max(self.size, self.max_size)

        # Need to do rebuild?
        if self._is_deep(depth):
            scapegoat = None
            parents.insert(0, node_to_add)
            sizes = [0]*len(parents)
            major_index = 0
            # find the highest scapegoat on the tree
            for minor_index in range(1, len(parents)):
                sizes[minor_index] = \
                    sizes[minor_index-1] + \
                    self._size_of(self._get_brother_of(parents[minor_index-1], parents[minor_index])) + \
                    1
                if not self.is_alpha_weight_balanced(parents[minor_index], sizes[minor_index]+1):
                    scapegoat = parents[minor_index]
                    major_index = minor_index

            tmp = self._rebuild_tree(scapegoat, sizes[major_index]+1)

            scapegoat.left = tmp.left
            scapegoat.right = tmp.right
            scapegoat.key = tmp.key
            scapegoat.value = tmp.value

    def is_alpha_weight_balanced(self, node, size_of_node):
        '''Is the tree alpha weight balanced?'''
        left = self._size_of(node.left) <= (self.alpha * size_of_node)
        right = self._size_of(node.right) <= (self.alpha * size_of_node)
        return left and right

    def preorder_traversal(self, visit=printfn, node=UNSPECIFIED):
        '''Traverse the tree in preorder.'''
        if node is UNSPECIFIED:
            node = self.root
        if node is not None:
            visit(node.key, node.value)
            self.preorder_traversal(visit, node.left)
            self.preorder_traversal(visit, node.right)

    def inorder_traversal(self, visit=printfn, node=UNSPECIFIED):
        '''Traverse the tree in inorder.'''
        if node is UNSPECIFIED:
            node = self.root
        if node is not None:
            self.inorder_traversal(visit, node.left)
            visit(node.key, node.value)
            self.inorder_traversal(visit, node.right)

    def postorder_traversal(self, visit=printfn, node=UNSPECIFIED):
        '''Traverse the tree in inorder.'''
        if node is UNSPECIFIED:
            node = self.root
        if node is not None:
            self.postorder_traversal(visit, node.left)
            self.postorder_traversal(visit, node.right)
            visit(node.key, node.value)

    def depth(self):
        '''Return the depth of the scapegoat tree'''
        class maxer(object):
            '''Class facilitates computing the maximum depth of all the treap (tree) branches'''
            def __init__(self, maximum=-1):
                self.max = maximum

            def feed(self, node, key, value, depth, from_left):
                # pylint: disable=R0913
                # R0913: We need a bunch of arguments
                '''Check our maximum so far against the current node - updating as needed'''
                dummy = node
                dummy = key
                dummy = value
                dummy = from_left
                if depth > self.max:
                    self.max = depth

            def result(self):
                '''Return the maximum we've found - plus one for human readability'''
                return self.max + 1

        max_obj = maxer()
        self.detailed_inorder_traversal(max_obj.feed)
        return max_obj.result()

    def keys(self):
        '''Yield the keys of the dictionary'''
        raise NotImplementedError

    def values(self):
        '''Yield the values of the dictionary'''
        raise NotImplementedError

    def items(self):
        '''Yield the key-value pairs of the dictionary'''
        raise NotImplementedError

    def _depth_and_field_width(self):
        '''Compute the depth of the tree and the maximum width within the nodes - for pretty printing'''
        class maxer(object):
            '''Class facilitates computing the max depth of the scapegoat tree and max width of the nodes'''
            def __init__(self, maximum=-1):
                self.depth_max = maximum
                self.field_width_max = -1

            def feed(self, node, key, value, depth, from_left):
                '''Check our maximums so far against the current node - updating as needed'''
                # pylint: disable=R0913
                # R0913: We need a bunch of arguments
                dummy = key
                dummy = value
                dummy = from_left
                if depth > self.depth_max:
                    self.depth_max = depth
                str_node = str(node)
                len_key = len(str_node)
                if len_key > self.field_width_max:
                    self.field_width_max = len_key

            def result(self):
                '''Return the maximums we've computed'''
                return (self.depth_max + 1, self.field_width_max)

        max_obj = maxer()
        self.detailed_inorder_traversal(max_obj.feed)
        return max_obj.result()

    def detailed_inorder_traversal(self, visit=printfn, node=UNSPECIFIED, depth=0, from_left=0):
        '''Do an inorder traversal - with lots of parameters'''
        if node is UNSPECIFIED:
            node = self.root
        if node.left is not None:
            self.detailed_inorder_traversal(visit, node.left, depth + 1, from_left * 2)
        visit(node, node.key, node.value, depth, from_left)
        if node.right is not None:
            self.detailed_inorder_traversal(visit, node.right, depth + 1, from_left * 2 + 1)

    def __str__(self):
        '''Format a scapegoat tree as a string'''
        class Desc(object):
            # pylint: disable=R0903
            # R0903: We don't need a lot of public methods
            '''Build a pretty-print string during a recursive traversal'''
            def __init__(self, pretree):
                self.tree = pretree

            def update(self, node, key, value, depth, from_left):
                '''Add a node to the tree'''
                # pylint: disable=R0913
                # R0913: We need a bunch of arguments
                dummy = key
                dummy = value
                self.tree[depth][from_left] = str(node)

        if self.root is None:
            # empty output for an empty tree
            return ''
        else:
            pretree = []
            depth, field_use_width = self._depth_and_field_width()
            field_use_width += 1
            for level in range(depth):
                string = '_' * (field_use_width - 1)
                pretree.append([string] * 2 ** level)
            desc = Desc(pretree)
            self.detailed_inorder_traversal(desc.update)
            result = []
            widest = 2 ** (depth - 1) * field_use_width
            for level in range(depth):
                two_level = 2 ** level
                field_avail_width = widest / two_level
                string = ''.join([center(x, field_use_width, field_avail_width) for x in desc.tree[level]])
                # this really isn't useful for more than dozen values or so, and that without priorities printed
                result.append(('%2d ' % level) + string)
            return '\n'.join(result)



    # These three things: keys, values, items; are a bit of a cheat.  In Python 2, they're really supposed to return lists,
    # but we return iterators like python 3.  A better implementation would check what version of python we're targetting,
    # give this behavior for python 3, and coerce the value returned to a list for python 2.
    def iterkeys(self):
        '''A macro for iterators - produces keys, values and items from almost the same code'''
        stack = [State('L', self.root)]

        while stack:
            state = stack.pop()
            if state.node is not None:
                if state.todo == 'V':
                    # yield state.node.key
                    yield state.node.key
                else:
                    if state.node.right is not None:
                        stack.append(State('R', state.node.right))
                    stack.append(State('V', state.node))
                    if state.node.left is not None:
                        stack.append(State('L', state.node.left))

    keys = iterator = __iter__ = iterkeys

    def itervalues(self):
        '''A macro for iterators - produces keys, values and items from almost the same code'''
        stack = [State('L', self.root)]

        while stack:
            state = stack.pop()
            if state.node is not None:
                if state.todo == 'V':
                    # yield state.node.key
                    yield state.node.value
                else:
                    if state.node.right is not None:
                        stack.append(State('R', state.node.right))
                    stack.append(State('V', state.node))
                    if state.node.left is not None:
                        stack.append(State('L', state.node.left))

    values = itervalues

    def iteritems(self):
        '''A macro for iterators - produces keys, values and items from almost the same code'''
        stack = [State('L', self.root)]

        while stack:
            state = stack.pop()
            if state.node is not None:
                if state.todo == 'V':
                    # yield state.node.key
                    yield state.node.key, state.node.value
                else:
                    if state.node.right is not None:
                        stack.append(State('R', state.node.right))
                    stack.append(State('V', state.node))
                    if state.node.left is not None:
                        stack.append(State('L', state.node.left))

    items = iteritems

    def reverse_iterator(self):
        '''Iterate over the nodes of the scapegoat tree in reverse order'''
        stack = [State('L', self.root)]

        while stack:
            state = stack.pop()
            if state.node is not None:
                if state.todo == 'V':
                    yield state.node.key
                else:
                    if state.node.left is not None:
                        stack.append(State('L', state.node.left))
                    stack.append(State('V', state.node))
                    if state.node.right is not None:
                        stack.append(State('R', state.node.right))


