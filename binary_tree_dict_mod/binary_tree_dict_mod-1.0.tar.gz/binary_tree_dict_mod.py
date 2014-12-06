#!/usr/local/cpython-3.3/bin/python



'''
Provides a binary tree class

Derived from http://www.laurentluce.com/posts/binary-search-tree-library-in-python/
'''

import sys
import math

SENTINEL = object()

def center(string, field_use_width, field_avail_width):
    '''Center a string within a given field width'''
    field_use = (string + '_' * (field_use_width - 1))[:field_use_width - 1]
    pad_width = (field_avail_width - len(field_use)) / 2.0
    result = ' ' * int(pad_width) + field_use + ' ' * int(math.ceil(pad_width))
    return result


def count_children(node):
    """
    Returns the number of children

    @returns number of children: 0, 1, 2
    """
    if node is SENTINEL:
        return SENTINEL
    count = 0
    if node.left is not SENTINEL:
        count += 1
    if node.right is not SENTINEL:
        count += 1
    return count


def nonrec_insert(node, key, value):
    """
    Insert new node with key, value - nonrecursively

    @param key node key object to insert
    """
    while True:
        if key < node.key:
            if node.left is SENTINEL:
                node.left = Node(key, value)
                return
            else:
                node = node.left
        elif key > node.key:
            if node.right is SENTINEL:
                node.right = Node(key, value)
                return
            else:
                node = node.right
        else:
            # key == node.key - replace
            node.key = key
            node.value = value
            # don't change node.left or node.right
            return


class Node(object):
    """
    Tree node: left and right child + key, value which can be any object
    """

    # conserve memory
    __slots__ = ('left', 'right', 'key', 'value')

    def __init__(self, key, value):
        """
        Node constructor

        @param key node data object
        """
        self.left = SENTINEL
        self.right = SENTINEL
        self.key = key
        self.value = value

    def __str__(self):
        return '%s/%s' % (self.key, self.value)

    def insert(self, key, value):
        """
        Insert new node with key

        @param key node key object to insert
        """
        nonrec_insert(self, key, value)

    def lookup(self, key, parent=SENTINEL):
        # pylint: disable=maybe-no-member
        """
        Lookup node containing key

        @param key node key object to look up
        @param parent node's parent
        @returns node and node's parent if found or SENTINEL, SENTINEL
        """
        if key < self.key:
            if self.left is SENTINEL:
                return SENTINEL, SENTINEL
            return self.left.lookup(key, self)
        elif key > self.key:
            if self.right is SENTINEL:
                return SENTINEL, SENTINEL
            return self.right.lookup(key, self)
        else:
            return self, parent

    def delete(self, key):
        # pylint: disable=too-many-branches
        """
        Delete node containing key

        @param key node's content to delete

        Return value: True if must remove root, False if not
        """
        # get node containing key
        node, parent = self.lookup(key)
        if node is SENTINEL:
            raise KeyError('Key not found')
        else:
            child_count = count_children(node)

            if child_count == 0:
                if parent is SENTINEL:
                    return True
                else:
                    # if node has no children, just remove it
                    if parent.left is node:
                        parent.left = SENTINEL
                    elif parent.right is node:
                        parent.right = SENTINEL
                    else:
                        raise AssertionError('Neither parent.left nor parent.right is node')
                    del node
                    return False
            elif child_count == 1:
                # if node has 1 child
                # replace node by its child
                if node.left is SENTINEL:
                    node2 = node.right
                elif node.right is SENTINEL:
                    node2 = node.left
                else:
                    raise AssertionError('Neither node.left nor node.right was SENTINEL')
                if parent is SENTINEL:
                    return True
                else:
                    if parent.left is node:
                        parent.left = node2
                    else:
                        parent.right = node2
                    return False
                del node
            elif child_count == 2:
                # if node has 2 children
                # find its successor
                parent = node
                successor = node.right
                while successor.left is not SENTINEL:
                    parent = successor
                    successor = successor.left
                # replace node key by its successor key
                node.key = successor.key
                node.value = successor.value
                # fix successor's parent's child
                if parent.left == successor:
                    parent.left = successor.right
                else:
                    parent.right = successor.right
                return False
            else:
                raise AssertionError('child_count is not in 0, 1, 2')

    def print_tree(self):
        # pylint: disable=maybe-no-member
        """
        Print tree content inorder
        """
        if self.left is not SENTINEL:
            self.left.print_tree()
        sys.stdout.write('%s ' % (self.key, ))
        if self.right is not SENTINEL:
            self.right.print_tree()

    def compare_trees(self, node):
        # pylint: disable=maybe-no-member
        """
        Compare 2 trees

        @param node tree's root node to compare to
        @returns True if the tree passed is identical to this tree
        """
        if node is SENTINEL:
            return False
        if self.key != node.key:
            return False
        res = True
        if self.left is SENTINEL:
            if node.left is not SENTINEL:
                return False
        else:
            res = self.left.compare_trees(node.left)
        if self.right is SENTINEL:
            if node.right is not SENTINEL:
                return False
        else:
            res = self.right.compare_trees(node.right)
        return res

    def inorder_traversal(self, visit):
        # pylint: disable=maybe-no-member
        '''Do an inorder traversal - without lots of parameters'''
        if self.left is not SENTINEL:
            self.left.inorder_traversal(visit)
        visit(self.key, self.value)
        if self.right is not SENTINEL:
            self.right.inorder_traversal(visit)

    def detailed_inorder_traversal(self, visit, depth=0, from_left=0):
        # pylint: disable=maybe-no-member
        '''Do an inorder traversal - with lots of parameters'''
        if self.left is not SENTINEL:
            self.left.detailed_inorder_traversal(visit, depth + 1, from_left * 2)
        visit(self, self.key, self.value, depth, from_left)
        if self.right is not SENTINEL:
            self.right.detailed_inorder_traversal(visit, depth + 1, from_left * 2 + 1)

    def items(self):
        """
        Generator to get the tree nodes data
        """
        # we use a stack to traverse the tree in a non-recursive way
        stack = []
        node = self
        while stack or node is not SENTINEL:
            if node is not SENTINEL:
                stack.append(node)
                node = node.left
            else: # we are returning so we pop the node and we yield it
                node = stack.pop()
                yield node.key, node.value
                node = node.right

    def depth(self):
        '''Return the depth of the tree, nonrecursively'''

        class Maxer(object):
            '''Compute the maximum depth of a tree via the detailed_inorder_traversal visit HoF'''
            def __init__(self):
                self.max_depth = 0

            def feed(self, node, key, value, depth, from_left):
                # pylint: disable=too-many-arguments
                '''
                Check if this depth is greater than the one we've memorized.
                If it is, keep it as the new max.
                '''
                dummy = node
                dummy = key
                dummy = value
                dummy = from_left
                if depth > self.max_depth:
                    self.max_depth = depth

            def get_depth(self):
                '''Getter method'''
                return self.max_depth

        max_obj = Maxer()

        self.detailed_inorder_traversal(visit=max_obj.feed)

        return max_obj.get_depth()

    def find_min(self):
        '''Find the minimum value in the tree'''

        node = self

        while node.left is not SENTINEL:
            node = node.left

        return node.key

    def find_max(self):
        '''Find the maximum value in the tree'''

        node = self

        while node.right is not SENTINEL:
            node = node.right

        return node.key

class BinaryTreeDict(object):
    '''Top level of a binary tree dict'''
    def __init__(self):
        self.root = SENTINEL

    def _depth_and_field_width(self):
        '''Compute the depth of the tree and the maximum width within the nodes - for pretty printing'''
        class maxer(object):
            '''Class facilitates computing the max depth of the binary tree and max width of the nodes'''
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

    def __str__(self):
        '''Format a binary tree as a string'''
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
            if self:
                self.root.detailed_inorder_traversal(desc.update)
            result = []
            widest = 2 ** (depth - 1) * field_use_width
            for level in range(depth):
                two_level = 2 ** level
                field_avail_width = widest / two_level
                string = ''.join([center(x, field_use_width, field_avail_width) for x in desc.tree[level]])
                # this really isn't useful for more than dozen values or so, and that without priorities printed
                result.append(('%2d ' % level) + string)
            return '\n'.join(result)

    def __bool__(self):
        if self.root is SENTINEL:
            return False
        else:
            return True

    __nonzero__ = __bool__

    def __setitem__(self, key, value):
        '''Insert data into dict'''
        if self.root is SENTINEL:
            self.root = Node(key, value)
        else:
            self.root.insert(key, value)

    def __getitem__(self, key):
        # pylint: disable=maybe-no-member
        '''Lookup data'''
        if self.root is SENTINEL:
            raise KeyError('key not found')
        else:
            current, parent = self.root.lookup(key)
            dummy = parent
            if current is SENTINEL:
                raise KeyError('key not found')
            else:
                return current.value

    def __delitem__(self, key):
        '''delete data'''
        if self.root is SENTINEL:
            raise KeyError('key not found')
        else:
            if self.root.delete(key):
                # We need to delete the root node...
                if self.root.left is SENTINEL:
                    if self.root.right is SENTINEL:
                        # Both left and right are SENTINEL.
                        self.root = SENTINEL
                    else:
                        # self.root.left is SENTINEL, but self.root.right is not.
                        self.root = self.root.right
                else:
                    if self.root.right is SENTINEL:
                        # self.root.left is not SENTINEL, but self.root.right is.
                        self.root = self.root.left
                    else:
                        # Both self.root.left and self.root.right are not SENTINEL.
                        # This is unexpected.
                        raise AssertionError('self.root.right and self.root.left are both SENTINEL in __delitem__')

    def print_tree(self):
        '''Print the tree'''
        if self.root is SENTINEL:
            return
        else:
            self.root.print_tree()

    def compare_trees(self, other):
        '''Compare two trees'''
        if self.root is SENTINEL:
            if other.root is SENTINEL:
                # Both are empty
                return True
            else:
                # self is empty, other is not
                return False
        else:
            if other.root is SENTINEL:
                # self is not empty, other is empty
                return False
            else:
                # neither are empty
                return self.compare_trees(other)

    def detailed_inorder_traversal(self, visit):
        '''Preform an inorder traversal of the binary tree, passing a little more detail to the visit function at each step'''
        if self.root is not SENTINEL:
            self.root.detailed_inorder_traversal(visit)

    def __len__(self):
        count = 0
        for dummy in self.keys():
            count += 1
        return count

    def depth(self):
        '''Return the depth of the tree'''
        if self.root is SENTINEL:
            return 0
        else:
            return self.root.depth()

    def find_min(self):
        '''Find the minimum element in the tree'''
        if self.root is SENTINEL:
            raise KeyError('tree is empty')
        else:
            return self.root.find_min()

    def find_max(self):
        '''Find the maximum element in the tree'''
        if self.root is SENTINEL:
            raise KeyError('tree is empty')
        else:
            return self.root.find_max()

    class state_class(object):
        # pylint: disable=R0903
        # R0903: We don't need a lot of public methods
        '''A state class, used for iterating over the nodes in a binary tree'''
        def __init__(self, todo, node):
            self.todo = todo
            self.node = node

        def __repr__(self):
            return '%s %s' % (self.todo, self.node)

    def inorder_traversal(self, visit):
        '''Inorder traversal - simple version'''
        self.root.inorder_traversal(visit)



    # These three things: keys, values, items; are a bit of a cheat.  In Python 2, they're really supposed to return lists,
    # but we return iterators like python 3.  A better implementation would check what version of python we're targetting,
    # give this behavior for python 3, and coerce the value returned to a list for python 2.
    def iterkeys(self):
        '''A macro for iterators - produces keys, values and items from almost the same code'''
        stack = [self.state_class('L', self.root)]

        while stack:
            state = stack.pop()
            if state.node is not SENTINEL:
                if state.todo == 'V':
                    # yield state.node.key
                    yield state.node.key
                else:
                    if state.node.right is not SENTINEL:
                        stack.append(self.state_class('R', state.node.right))
                    stack.append(self.state_class('V', state.node))
                    if state.node.left is not SENTINEL:
                        stack.append(self.state_class('L', state.node.left))

    keys = iterator = __iter__ = iterkeys

    def itervalues(self):
        '''A macro for iterators - produces keys, values and items from almost the same code'''
        stack = [self.state_class('L', self.root)]

        while stack:
            state = stack.pop()
            if state.node is not SENTINEL:
                if state.todo == 'V':
                    # yield state.node.key
                    yield state.node.value
                else:
                    if state.node.right is not SENTINEL:
                        stack.append(self.state_class('R', state.node.right))
                    stack.append(self.state_class('V', state.node))
                    if state.node.left is not SENTINEL:
                        stack.append(self.state_class('L', state.node.left))

    values = itervalues

    def iteritems(self):
        '''A macro for iterators - produces keys, values and items from almost the same code'''
        stack = [self.state_class('L', self.root)]

        while stack:
            state = stack.pop()
            if state.node is not SENTINEL:
                if state.todo == 'V':
                    # yield state.node.key
                    yield state.node.key, state.node.value
                else:
                    if state.node.right is not SENTINEL:
                        stack.append(self.state_class('R', state.node.right))
                    stack.append(self.state_class('V', state.node))
                    if state.node.left is not SENTINEL:
                        stack.append(self.state_class('L', state.node.left))

    items = iteritems

    def reverse_iterator(self):
        '''Iterate over the nodes of the binary tree in reverse order'''
        stack = [self.state_class('L', self.root)]

        while stack:
            state = stack.pop()
            if state.node is not SENTINEL:
                if state.todo == 'V':
                    yield state.node.key
                else:
                    if state.node.left is not SENTINEL:
                        stack.append(self.state_class('L', state.node.left))
                    stack.append(self.state_class('V', state.node))
                    if state.node.right is not SENTINEL:
                        stack.append(self.state_class('R', state.node.right))


