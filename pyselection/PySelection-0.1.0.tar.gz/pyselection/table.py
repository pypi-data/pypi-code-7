#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
"""Classes for tabular data."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import MutableSequence
from copy import copy, deepcopy
from types import NoneType

from pyselection import core
from pyselection.core import int_types
from pyselection.core import str_types
from pyselection.core import is_sized_iterable
from pyselection.core import range

class BaseList(MutableSequence):
    
    @classmethod
    def validate_data_types(this, data_types):
        if not isinstance(data_types, tuple):
            raise TypeError("%s data types must be specified as a tuple" % 
              this.__name__)
        data_types = set(data_types)
        if any( x not in core.table_data_types for x in data_types ):
            raise TypeError("%s data types must be one or more of %s" % 
                  (this.__name__, str( tuple(x.__name__ 
                  for x in core.table_data_types) ) ) )
        data_types.add(NoneType)
        return tuple( sorted( list(data_types) ) )

    @property
    def data_types(self):
        return self._dtypes
    
    @property
    def nom(self):
        return repr(self.__class__.__name__)
    
    def __init__(self, contents, data_types=None):

        if data_types is not None:
            self._dtypes = self.__class__.validate_data_types(data_types)
        else:
            self._dtypes = core.table_data_types 
        
        self.validate_list(contents)
            
        self._list = [ x for x in contents ]

    def __add__(self, other):
        try:
            if isinstance(other, BaseList):
                self._verify_combinable(other)
            else:
                other = self.__class__(other, data_types=self._dtypes)
        except TypeError:
            raise TypeError("cannot combine objects of type %s and %s" % 
                  (self.nom, repr(type(other).__name__) ) )
        
        if type(other) == type(self):
            return self.__class__(self._list + other._list, data_types=self._dtypes)
        else:
            return other.__radd__(self)

    def __bool__(self):
        return len(self._list) != 0

    def __contains__(self, value):
        return value in self._list

    def __copy__(self):
        return self.__class__(copy(self._list), data_types=self._dtypes) 

    def __deepcopy__(self, memo=dict() ):
        return self.__class__(deepcopy(self._list, memo), data_types=self._dtypes)

    def __delitem__(self, key):
        
        if isinstance(key, int_types):
            
            index = self._adapt_index(key)
            del self._list[index]
        
        elif isinstance(key, slice):
            
            slc = self._adapt_slice(key)
            del self._list[slc]
            
        else:
            raise TypeError("invalid %s key (%s)" % (self.nom, repr(key)))

    def __eq__(self, other):
    
        try:
            if not isinstance(other, BaseList):
                other = self.__class__(other, data_types=self._dtypes)
        except TypeError:
            return False
        
        if type(other) != type(self) and issubclass(type(other), BaseList):
            return other.__eq__(self)
        else:
            return self._dtypes == other._dtypes and self._list == other._list

    def __getitem__(self, key):

        if isinstance(key, int_types):
            
            item = self.get_element(key)
        
        elif isinstance(key, slice):
            
            item = self.get_slice(key)
            
        else:
            raise TypeError("invalid %s key (%s)" % (self.nom, repr(key)))
        
        return item

    def __iadd__(self, other):
    
        try:
            if not isinstance(other, BaseList):
                other = self.__class__(other, data_types=self._dtypes)
            elif type(other) == type(self):
                self._verify_combinable(other)
            else:
                raise TypeError
        except TypeError:
            raise TypeError("cannot append %s to %s" % 
              (repr(type(other).__name__) ), self.nom)
        
        self = self.__class__(self._list + other._list, data_types=self._dtypes)
        return self
        
    def __iter__(self):

        for x in self._list:
            yield x

    def __len__(self):
        return len(self._list)

    def __ne__(self, other):
        return not self == other

    def __nonzero__(self):
        return type(self).__bool__(self)

    def __radd__(self, other):

        try:
            if isinstance(other, BaseList):
                self._verify_combinable(other)
            else:
                other = self.__class__(other, data_types=self._dtypes)
        except TypeError:
            raise TypeError("cannot combine objects of type %s and %s" % 
              (repr(type(other).__name__), self.nom) )
        
        if type(other) == type(self):
            return self.__class__(other._list + self._list, data_types=self._dtypes)
        else:
            return other.__add__(self)

    def __reversed__(self):

        for x in reversed(self._list):
            yield x

    def __setitem__(self, key, value):
        
        if isinstance(key, int_types):
            
            self.set_element(key, value)
        
        elif isinstance(key, slice):
            
            self.set_slice(key, value)
            
        else:
            raise TypeError("invalid %s key (%s)" % (self.nom, repr(key) ) )
    
    def __str__(self):
        contents = "(%s)" % ", ".join( repr(x) for x in self._list )
        return "%s%s" % (self.nom, contents)

    def _adapt_index(self, index):
        
        if not isinstance(index, int_types):
            raise IndexError("%s index (%s) must be an integer" % (self.nom, repr(index) ) )
        length = len(self._list)
            
        if index < -length or index >= length:
            raise IndexError("%s index (%d) out of range" % (self.nom, index) )
        if index < 0:
            index += length
        return index

    def _adapt_slice(self, slc, properties=None):
        
        try:
            if not all( isinstance(x, tuple([int_types] + [NoneType]) ) 
                for x in (slc.start, slc.stop, slc.step) ):
                    raise TypeError("%s slice indices must be integer or None" % self.nom)
        except AttributeError:
            raise TypeError("%s _adapt_slice() takes a slice object" % self.nom)
    
        length = len(self._list)
    
        if slc.step is None:
            step = 1
        elif slc.step != 0:
            step = slc.step
        else:
            raise ValueError("%s slice step cannot be zero" % self.nom)
 
        if slc.start is not None:
            start = slc.start
            if start < -length or start >= length:
                raise IndexError("%s slice start (%d) out of range" % (self.nom, start) )
            if start < 0:
                start += length
        else:
            start = 0 if step > 0 else length - 1

        if slc.stop is not None:
            stop = slc.stop
            if stop < -length or stop > length:
                raise IndexError("%s slice stop (%d) out of range" % (self.nom, stop) )
            if stop < 0:
                stop += length
            if step == 1:
                if start > stop:
                    stop = start
            elif (step > 1 and start >= stop) or (step < 0 and start <= stop):
                raise ValueError("%s extended slice is of size 0" % self.nom)
        else:
            stop = length if step > 0 else -1
    
        if properties is not None:
        
            step_quotient, step_remainder = divmod( abs(stop - start), abs(step) )
        
            if step_remainder:
                if step > 0:
                    last = stop - step_remainder
                else:
                    last = stop + step_remainder
                size = step_quotient + 1
            else:
                last = stop - step
                size = step_quotient
     
            try:
                properties['last'] = last
                properties['size'] = size
                properties['min'], properties['max'] = sorted([start, last])
                properties['span'] = properties['max'] - properties['min'] + 1
            except TypeError:
                raise TypeError("%s _adapt_slice() properties object must be a dict" % self.nom)
        
        return slice(start, stop, step)

    def _verify_combinable(self, other):
    
        try:
            if self._dtypes != other._dtypes:
                raise ValueError("cannot combine %s and %s (data type mismatch)" % 
                  (self.nom, other.nom) )
                
            if type(other) != type(self):
                for x in other:
                    self.validate_element(x)
                    
        except (AttributeError, TypeError):
            raise TypeError("cannot combine objects of type %s and %s" % 
                  (self.nom, repr(type(other).__name__) ) )

    def append(self, value):

        i = len(self._list)
        self[i:i] = [ value ]

    def count(self, value, start=None, stop=None):

        indices = self.iter_indices(start=start, stop=stop)
        return sum( 1 if self._list[i] == value else 0 for i in indices )
    
    def extend(self, values):
    
        i = len(self._list)
        self[i:i] = values
    
    def findall(self, value, start=None, stop=None):

        indices = self.iter_indices(start=start, stop=stop)
        return tuple( i for i in indices if self._list[i] == value )

    def get_element(self, index):
    
        index = self._adapt_index(index)
        return self._list[index]
            
    def get_slice(self, key):

        slc = self._adapt_slice(key)
        return self.__class__(self._list[slc], data_types=self._dtypes)

    def index(self, value, start=None, stop=None):

        indices = self.iter_indices(start=start, stop=stop)
        for i in indices:
            if self._list[i] == value:
                return i
        raise ValueError("value (%s) not found" % repr(value) )

    def insert(self, index, value):

        self[index:index] = [ value ]

    def iter_indices(self, start=None, stop=None, reverse=False):
        
        length = len(self._list)
    
        if start is not None:
            if not isinstance(start, int_types):
                raise IndexError("%s start index (%s) must be an integer" % 
                  (self.nom, repr(start) ) )
            if start < -length or start >= length:
                raise IndexError("%s start index (%d) out of range" % 
                  (self.nom, start) )
            if start < 0:
                start += length
        else:
            start = 0
            
        if stop is not None:
            if not isinstance(stop, int_types):
                raise IndexError("%s stop index (%s) must be an integer" % 
                  (self.nom, repr(stop) ) )
            if stop < -length or stop > length:
                raise IndexError("%s stop index (%d) out of range" % 
                  (self.nom, stop) )
            if stop < 0:
                stop += length
        else:
            stop = length          
            
        if start >= stop:
            raise IndexError("%s iteration range has length zero" % self.nom)
    
        if not reverse:
            for i in range(start, stop):
                yield i
        else:
            for i in reversed( range(start, stop) ):
                yield i

    def pop(self):

        return self._list.pop()

    def reverse(self):

        self._list.reverse()

    def rindex(self, value, start=None, stop=None):

        indices = self.iter_indices(start=start, stop=stop, reverse=True)
        for i in indices:
            if self._list[i] == value:
                return i
        raise ValueError("value (%s) not found" % repr(value) )

    def set_element(self, index, value):
        
        index = self._adapt_index(key)
        self.validate_element(value)
        self._list[index] = value

    def set_slice(self, key, value): 
    
        slc_info = dict()
            
        slc = self._adapt_slice(key, slc_info)
                    
        try:
            value_length = len(value)
        except TypeError:
            raise TypeError("%s slice value must be a sized iterable" % self.nom)
        
        if slc.step != 1:
            if value_length != slc_info['size']:
                raise ValueError("cannot assign %d values to extended slice "
                  "of size %d" % (value_length, slc_info['size']) )
        
        self.validate_list(value)
        
        self._list[slc] = value
  
    def tolist(self):

        return [ x for x in self._list ]

    def validate_element(self, value):
        if not isinstance(value, self._dtypes):
            dtype_names = str( tuple(x.__name__ for x in self._dtypes) ) 
            raise TypeError("%s element data type must be one or more of %s" % 
              (self.nom, dtype_names) )

    def validate_list(self, values):
        
        if isinstance(values, BaseList):
            if all( x in self._dtypes for x in values._dtypes ):
                return
        elif not is_sized_iterable(values) or isinstance(values, str_types):
            raise TypeError("%s list must be a sized non-string iterable" % self.nom)
        if not all( isinstance(value, self._dtypes) for value in values ):
            dtype_names = str( tuple(x.__name__ for x in self._dtypes) ) 
            raise TypeError("%s element data types must be one or more of %s" % 
              (self.nom, dtype_names) )

################################################################################

class BaseTable(BaseList):

    @classmethod
    def validate_row_type(this, row_type):
        if not issubclass(row_type, BaseList) or issubclass(row_type, BaseTable):
            raise TypeError("BaseTable row type must be a BaseList but not BaseTable")

    @property
    def data_types(self):

        return self._dtypes   
    @property
    def max_row_length(self):
        return self._max_row_length

    @property
    def min_row_length(self):
        return self._min_row_length    
    
    @property
    def row_lengths(self):

        return self._row_lengths

    def __init__(self, contents, data_types=None, row_type=None, row_labels=None):

        if data_types is not None:
            self._dtypes = self.__class__.validate_data_types(data_types)
        else:
            self._dtypes = core.table_data_types
        
        if row_type is not None:
            self.__class__.validate_row_type(row_type)
            self._rtype = row_type
        else:
            self._rtype = BaseList
            
        self._list = [ self._rtype(row, data_types=self._dtypes) 
          for row in contents ]
        
        if row_labels is not None:
            self.row_labels = row_labels

    def __add__(self, other):

        try:
            if isinstance(other, BaseTable):
                self._verify_combinable(other)
            else:
                other = self.__class__(other, data_types=self._dtypes, 
                  row_type=self._rtype)
        except TypeError:
            raise TypeError("cannot catenate objects of type %s and %s" % 
                  (self.nom, repr(type(other).__name__) ) )
        
        if type(other) == type(self):
            item = deepcopy(self)
            item.extend(other)
            return item
        else:
            return other.__radd__(self)

    def __contains__(self, value): 
        if isinstance(value, self._dtypes):
            return any( value in row for row in self._list )
        else:
            return value in self._list

    def __copy__(self):

        if hasattr(self, "row_labels"):
            row_labels = copy(self.row_labels)
        else:
            row_labels = None
            
        return self.__class__(copy(self._list), data_types=self._dtypes, 
          row_type=self._rtype, row_labels=row_labels) 
 
    def __deepcopy__(self, memo=dict() ):
        
        if hasattr(self, "row_labels"):
            row_labels = deepcopy(self.row_labels)
        else:
            row_labels = None
        
        return self.__class__([ deepcopy(x, memo) for x in self._list ], 
          data_types=deepcopy(self._dtypes, memo), 
          row_type=deepcopy(self._rtype, memo),
          row_labels=row_labels )

    def __delitem__(self, key):
    
        if isinstance(key, int_types):
            
            index = self._adapt_index(key)
            del self._list[index]
            
        elif isinstance(key, slice):
            
            slc = self._adapt_slice(key)
            del self._list[slc]
              
        elif isinstance(key, tuple):
            
            try:
                row_key, col_key = key
            except ValueError:
                raise TypeError("too many %s indices/keys" % self.nom)
            
            slicer = TableSlicer(self, row_key, col_key)
            
            for r in slicer.iter_rows_decreasing():
                del self._list[r][ slicer.col_slice ]
            
        else:
            raise TypeError("invalid %s index/key (%s)" % (self.nom, repr(key) ) )
        
        # Clear row lengths so they will be recalculated.
        self._clear_row_lengths()

    def __eq__(self, other):

        try:
            if not isinstance(other, BaseTable):
                other = BaseTable(other, data_types=self._dtypes, 
                  row_type=self._rtype)
        except TypeError:
            return False
        
        if type(other) != type(self) and issubclass(type(other), BaseTable):
            return other.__eq__(self)
        else:
            if self._dtypes != other._dtypes:
                return False
                
            if self._rtype != other._rtype:
                return False
                
            if self._list != other._list:
                return False
            
            self_labels = self.row_labels if hasattr(self, "row_labels") else None
            other_labels = other.row_labels if hasattr(other, "row_labels") else None
            
            if self_labels != other_labels:
                return False
                
            return True

    def __getattr__(self, attr):
    
        if attr in ("_row_lengths", "_min_row_length", "_max_row_length"):
            self._update_row_lengths()
            return getattr(self, attr)
            
        elif attr == "row_labels":
            
            self.row_labels = TableLabels.from_length( len(self._list) )
            return self.row_labels
            
        else:
            raise AttributeError("%s object has no attribute called %s" % 
              (self.nom, attr) )

    def __getitem__(self, key):
        
        item = None
        
        if isinstance(key, int_types):
            
            item = self.get_element(key)
            
        elif isinstance(key, slice):
            
            item = self.get_slice(key)
            
        elif isinstance(key, tuple):
            
            try:
                row_key, col_key = key
            except ValueError:
                raise TypeError("too many %s indices/keys" % self.nom)
            
            if all( isinstance(x, int_types) for x in key ):
                
                item = self.get_table_element(row_key, col_key)
                
            else:
                
                item = self.get_table_slice(row_key, col_key)
            
        else:
            raise TypeError("invalid %s index/key (%s)" % (self.nom, repr(key) ) )
        
        return item

    def __iadd__(self, other):

        try:
            if not isinstance(other, BaseTable):
                other = self.__class__(other, data_types=self._dtypes, 
                  row_type=self._rtype)
            elif type(other) == type(self):
                self._verify_combinable(other)
            else:
                raise TypeError
        except TypeError:
            raise TypeError("cannot append %s to %s" % 
              (repr(type(other).__name__) ), self.nom)
        
        self.extend(other)
        return self

    def __ne__(self, other):
    
        return not self == other

    def __radd__(self, other):

        try:
            if isinstance(other, BaseTable):
                self._verify_combinable(other)
            else:
                other = self.__class__(other, data_types=self._dtypes, 
                  row_type=self._rtype)
        except TypeError:
            raise TypeError("cannot catenate objects of type %s and %s" % 
              (repr(type(other).__name__) ), self.nom)
        
        if type(other) == type(self):
            item = deepcopy(other)
            item.extend(self)
            return item
        else:
            return other.__add__(self)

    def __setattr__(self, attr, value):
        
        if attr == "row_labels":
            if value is not None:
                if not isinstance(value, TableLabels):
                    raise TypeError("%s row labels must be of type TableLabels" % self.nom)
                elif len(value) != len(self._list):
                    raise ValueError("number of %s row labels must match number of rows" % self.nom)

        self.__dict__[attr] = value
     
    def __setitem__(self, key, value):
        
        if isinstance(key, int_types):
            
            self.set_element(key, value)
            
        elif isinstance(key, slice):
            
            self.set_slice(key, value)
            
        elif isinstance(key, tuple):
            
            try:
                row_key, col_key = key
            except ValueError:
                raise TypeError("too many %s indices/keys" % self.nom)
            
            if all( isinstance(x, int_types) for x in key ):
                
                self.set_table_element(row_key, col_key, value)
                
            else:
                
                self.set_table_slice(row_key, col_key, value)
                
        else:
            raise TypeError("invalid %s index/key (%s)" % (self.nom, repr(key) ) )

    def __str__(self):

        contents = "(\n  %s\n)" % ",\n  ".join( str(x) for x in self._list)
        return "%s(\n  %s\n)" % (self.nom, contents)

    def _adapt_index2(self, index):
    
        if not isinstance(index, int_types):
            raise IndexError("%s index (%s) must be an integer" % (self.nom, repr(index) ) )
        
        length = self.max_row_length
        
        diff_lengths = self.min_row_length != length

        if index < -length or index >= length:
            raise IndexError("%s index (%d) out of range" % (self.nom, index ) )   
    
        if index < 0:
            if length:
                raise ValueError("cannot use negative index (%d) in jagged %s" % (index, self.nom) )
            index += length    
    
        return index

    def _adapt_slice2(self, slc, properties=None):

        try:
            if not all( isinstance(x, tuple([int_types] + [NoneType]) ) 
                for x in (slc.start, slc.stop, slc.step) ):
                    raise TypeError("%s slice indices must be integer or None" % basetable.nom)
        except AttributeError:
            raise TypeError("%s _adapt_slice2() takes a slice object" % self.nom)

        length = self.max_row_length
        diff_lengths = self.min_row_length != length
        
        if slc.step is None:
            step = 1
        elif slc.step != 0:
            step = slc.step
        else:
            raise ValueError("%s slice step cannot be zero" % self.nom)    

        if slc.start is not None:
    
            start = slc.start
        
            if start < -length or start >= length:
                raise IndexError("%s slice start (%d) out of range" % (self.nom, start) )
            if start < 0:
                if diff_lengths:
                    raise ValueError("cannot use negative start index (%d) in jagged %s" % (start, self.nom) )
                start += length         
        else:
            if step > 0:
                start = 0
            elif not diff_lengths: 
                start = length - 1
            else:
                raise ValueError("cannot set default start index of negative stepping slice in jagged %s" % self.nom)
        
        if slc.stop is not None:
        
            stop = slc.stop
        
            if stop < -length or stop > length:
                raise IndexError("%s slice stop (%d) out of range" % (self.nom, stop) )
            if stop < 0:
                if diff_lengths:
                    raise ValueError("cannot use negative stop index (%d) in jagged %s" % (stop, self.nom) )
                stop += length
        
            if step == 1:
                if start > stop:
                    stop = start
            elif (step > 1 and start >= stop) or (step < 0 and start <= stop):
                raise ValueError("%s extended slice is of size 0" % self.nom)
        else:
            if step < 0:
                stop = -1
            elif not diff_lengths:   
                stop = length
            else:
                raise ValueError("cannot set default stop index in jagged %s" % self.nom)
    
        if properties is not None:
              
            step_quotient, step_remainder = divmod( abs(stop - start), abs(step) )
        
            if step_remainder:
                if step > 0:
                    last = stop - step_remainder
                else:
                    last = stop + step_remainder
                size = step_quotient + 1
            else:
                last = stop - step
                size = step_quotient

            try:
                properties['last'] = last
                properties['size'] = size
                properties['min'], properties['max'] = sorted([start, last])
                properties['span'] = properties['max'] - properties['min'] + 1
            except TypeError:
                raise TypeError("%s _adapt_slice2() properties object must be a dict" % self.nom)
        
        return slice(start, stop, step)

    def _clear_row_lengths(self):
    
        try:
            del self._row_lengths
            del self._min_row_length
            del self._max_row_length
        except AttributeError:
            pass

    def _update_row_lengths(self):
        
        self._row_lengths = tuple( len(x) for x in self._list )
        
        try:
            self._min_row_length = min(self._row_lengths)
            self._max_row_length = max(self._row_lengths)
        except ValueError:
            self._min_row_length, self._max_row_length = None, None

    def _verify_combinable(self, other):
    
        try:
            if self._dtypes != other._dtypes:
                raise ValueError("cannot combine %s and %s (data type mismatch)" % 
                  (self.nom, other.nom) )

            if self._rtype != other._rtype:
                raise ValueError("cannot combine %s and %s (row type mismatch)" % 
                  (self.nom, other.nom) )
                      
            if type(other) != type(self):
                for x in other:
                    self.validate_list(x)
                    
        except (AttributeError, TypeError):
            raise TypeError("cannot combine objects of type %s and %s" % 
                  (self.nom, repr(type(other).__name__) ) )

    def append(self, value):

        i = len(self._list)
        self[i:i] = [ self._rtype(value, data_types=self._dtypes) ]
        
    def count(self, value, start=None, stop=None):

        if isinstance(value, self._dtypes):
            indices = self.iter_indices(start=start, stop=stop)
            return sum( 1 if self._list[r][c] == value else 0 
              for r, c in indices )
        else:
            return super(BaseTable, self).count(value, start=start, stop=stop)
    
    def extend(self, values):
    
        i = len(self._list)
        self[i:i] = self.__class__(values, data_types=self._dtypes)
    
    def findall(self, value, start=None, stop=None):

        if isinstance(value, self._dtypes):
            indices = self.iter_indices(start=start, stop=stop)
            return tuple( (r, c) for r, c in indices 
              if self._list[r][c] == value )
        else:
            return super(BaseTable, self).findall(value, start=start, stop=stop)
    
    def get_element(self, row_index):

        r = self._adapt_index(row_index)
        return self._rtype(self._list[r], data_types=self._dtypes)
            
    def get_slice(self, row_key):

        slc = self._adapt_slice(row_key)
        
        if hasattr(self, "row_labels") and any(x for x in self.row_labels[slc]):
            row_labels = self.row_labels[slc]
        else:
            row_labels = None
        
        item = self.__class__(self._list[slc], data_types=self._dtypes, 
          row_type=self._rtype, row_labels=row_labels)
        
    def get_table_element(self, row_index, col_index):

        
        r = self._adapt_index(row_index)
        c = self._adapt_index2(col_index)
                
        try:
            item = self._list[r][c]
        except TypeError:
            raise IndexError("%s index (%d, %d) out of range" % (self.nom, r, c) )

        return item

    def get_table_slice(self, row_key, col_key):


        slicer = TableSlicer(self, row_key, col_key)
                
        rows = list()
                
        for r in slicer.iter_rows():
            
            row = list()
            
            for c in slicer.iter_cols():
                
                try:
                    x = self._list[r][c]
                except TypeError:
                    x = None
                
                row.append(x)
            
            rows.append(row)
            
        if slicer.size[0] > 1:
            item = self.__class__(rows, data_types=self._dtypes, row_type=self._rtype)
        else:
            item = self._rtype(rows[0], data_types=self._dtypes)

        return item

    def index(self, value, start=None, stop=None):

        if isinstance(value, self._dtypes):
            indices = self.iter_indices(start=start, stop=stop)
            for r, c in indices:
                if self._list[r][c] == value:
                    return (r, c)
        else:
            return super(BaseTable, self).index(value, start=start, stop=stop)
            
        raise ValueError("value not in %s" % self.nom)

    def insert(self, index, value):

        self[index:index] = self._rtype(value, data_types=self._dtypes)

    def iter_indices(self, start=None, stop=None, reverse=False):

        table_length = len(self._list)
        row_lengths = self._row_lengths

        if start is not None:
            
            try:
                start_row, start_col = start
                assert all( isinstance(x, int_types) for x in start )
            except (AssertionError, ValueError):
                raise TypeError("%s start argument must be a tuple of two integers" % self.nom)
            
            if start_row < -table_length or start_row >= table_length:
                raise IndexError("%s start row index (%d) out of range" % (self.nom, start_row) )
            if start_row < 0:
                start_row += table_length
            
            start_row_length = row_lengths[start_row]
            if start_col < -start_row_length or start_col >= start_row_length:
                raise IndexError("%s start column index (%d) out of range" % (self.nom, start_col) )
            if start_col < 0:
                start_col += start_row_length
        else:
            start_row, start_col = (0, 0)

        if stop is not None:
        
            try:
                stop_row, stop_col = stop
                assert all( isinstance(x, int_types) for x in stop )
            except (AssertionError, ValueError):
                raise TypeError("%s stop argument must be a tuple of two integers" % self.nom)
    
            if stop_row < -table_length or stop_row > table_length:
                raise IndexError("%s stop row index (%d) out of range" % (self.nom, stop_row) )
            if stop_row < 0:
                stop_row += table_length
        
            last_row_length = row_lengths[stop_row - 1]
            if stop_col < -last_row_length or stop_col > last_row_length:
                raise IndexError("%s stop column index (%d) out of range" % (self.nom, stop_col) )
            if stop_col < 0:
                stop_col += last_row_length
        else:
            stop_row, stop_col = (table_length, row_lengths[-1])
        
        last_row = stop_row - 1

        if stop_col == 0:
            stop_row, last_row = stop_row - 1, last_row - 1
            stop_col = row_lengths[last_row]

        if start_row > last_row or (start_row == last_row and 
          start_col >= stop_col):
            raise ValueError("%s has range zero" % self.nom)
        
        if not reverse:
            
            i, j = start_row, start_col
            while i < last_row or ( i == last_row and j < stop_col ):
                if j < row_lengths[i]:
                    yield (i, j)
                    j += 1
                else:
                    i, j = (i+1, 0)
        else:
            
            i, j = last_row, stop_col - 1
            while i > start_row or ( i == start_row and j >= start_col ):
                if j >= 0:
                    yield (i, j)
                    j -= 1
                else:
                    i, j = (i-1, row_lengths[i-1] - 1)
   
    def pop(self):
    
        if hasattr(self, "row_labels"):
            self.row_labels = TableLabels( self.row_labels[:-1] )
        self._clear_row_lengths()
        return self._list.pop()

    def reverse(self):

        if hasattr(self, "row_labels"):
            self.row_labels = TableLabels([x for x in reversed(self.row_labels)])
        self._clear_row_lengths()
        self._list.reverse()
        
    def rindex(self, value, start=None, stop=None):

        if isinstance(value, self._dtypes):
            rindices = self.iter_indices(start=start, stop=stop, reverse=True)
            for r, c in rindices:
                if self._list[r][c] == value:
                    return (i, j)
        else:
            return super(BaseTable, self).rindex(value, start=start, stop=stop)

        raise ValueError("value not in %s" % self.nom)    
  
    def set_element(self, row_index, value):
    
        r = self._adapt_index(row_index)
        self._list[r] = self._rtype(value, data_types=self._dtypes)
        self._clear_row_lengths()
        
    def set_slice(self, row_key, value):   
        
        slc_info = dict()
                
        slc = self._adapt_slice(row_key, slc_info)
        
        try:
            value_length = len(value)
        except TypeError:
            raise TypeError("%s slice value must be a sized iterable" % self.nom)
            
        if slc.step != 1:
            if value_length != slc_info['size']:
                raise ValueError("cannot assign %d rows to extended slice "
                  "of size %d" % (value_length, slc_info['size']) )
        
        self._list[slc] = [ self._rtype(x, data_types=self._dtypes) 
           for x in value ]
        
        if any( hasattr(x, "row_labels") for x in (self, value) ):
            
            tlabels = list(self.row_labels)
            
            try:
                vlabels = list(value.row_labels)
            except AttributeError:
                vlabels = [''] * value_length
            
            tlabels[slc] = vlabels
            self.row_labels = TableLabels(tlabels)
        
        self._clear_row_lengths()
        
    def set_table_element(self, row_index, col_index, value):
        
        r = self._adapt_index(row_index)
        c = self._adapt_index2(col_index)
        
        self.validate_element(value)
        
        try:
            self._list[r][c] = value
        except TypeError: # if column index is None
            raise IndexError("%s index (%d, %d) out of range" % (self.nom, r, c) )

    def set_table_slice(self, row_key, col_key, value):

        slicer = TableSlicer(self, row_key, col_key)
                
        if slicer.size[0] == 1:
            value = [ value ]
            
        value = self.__class__(value, data_types=self._dtypes)
        
        table_row_lengths = self._row_lengths
        value_row_lengths = value.row_lengths
        
        if len(value) != slicer.size[0]:
            raise ValueError("cannot use double-indexing to create/delete rows")
        
        if isinstance(col_key, int_types):
            if any( l != 1 for l in value_row_lengths ):
                raise ValueError("cannot assign multi-column value to "
                  "single %s column" % self.nom)
        elif slicer.step[1] != 1:
            if any( l != slicer.size[1] for l in value_row_lengths ):
                raise ValueError("cannot assign jagged rows to extended slice")
            
        for i, r in enumerate( slicer.iter_rows() ):
            
            row_length = table_row_lengths[r]
            
            if slicer.max[1] >= row_length:
        
                if abs(slicer.step[1]) != 1:
                    if slicer.max[1] > row_length:
                        raise ValueError("cannot assign to disjoint extended slice")
                elif slicer.min[1] > row_length:
                    raise ValueError("cannot assign to disjoint slice")
                
                self._list[r].extend([None] * (slicer.max[1] + 1 - row_length) )
        
            self._list[r][ slicer.col_slice ] = value[i]
        
        self._clear_row_lengths()
   
    def tolist(self, flatten=False):

        if flatten:
            return [ x for row in self._list for x in row ] 
        else:
            return [ list(x) for x in self._list ]

    def validate_table(self, table):
    
        if isinstance(table, BaseTable):
            if all( x in self._dtypes for row in table for x in row._dtypes ):
                return
        elif not is_sized_iterable(table) or isinstance(table, str_types):
            raise TypeError("%s table must be a sized non-string iterable" % self.nom)
        
        for row in table:
            
            if isinstance(row, BaseList):
                if all( x in self._dtypes for x in row._dtypes ):
                    continue
            elif not is_sized_iterable(row) or isinstance(row, str_types):
                raise TypeError("%s row must be a sized non-string iterable" % self.nom)            
            
            if not all( isinstance(value, self._dtypes) for value in row ):
                dtype_names = str( tuple(x.__name__ for x in self._dtypes) ) 
                raise TypeError("%s element data types must be one or more of %s" % 
                  (self.nom, dtype_names) )

class TableLabels(MutableSequence):
    
    @classmethod
    def from_length(this, length):
        try:
            return this([''] * length)
        except TypeError:
            raise TypeError("%s length (%s) must be an integer" % (self.nom, length) )

    @property
    def nom(self):
        return self.__class__.__name__

    def __init__(self, labels):
        
        try:
            assert len(labels) > 0
            assert not isinstance(labels, str_types)
            assert all( isinstance(x, str_types) for x in labels )
            
        except (AssertionError, TypeError):
            raise TypeError("%s() takes a sized iterable of strings" % self.nom)
       
        self._labels = labels
        
        self._label2index = dict()
        
        for index, label in enumerate(labels):
            
            if label != '':
                
                if label in self._label2index:
                    raise ValueError("%s cannot contain duplicate labels" % self.nom)
            
                self._label2index[label] = index

    def __bool__(self):
        return len(self._labels) != 0  
  
    def __contains__(self, value):
        return value in self._labels
  
    def __copy__(self):
        return self.__class__( copy(self._labels) ) 
  
    def __deepcopy__(self, memo=dict() ):
        return self.__class__( deepcopy(self._labels, memo) )  
  
    def __delitem__(self, key, value):       
        raise TypeError("%s cannot be resized" % self.nom)
        
    def __eq__(self, other):
        if isinstance(other, TableLabels):
            return self._labels == other._labels
        try:
            return self._labels == TableLabels(other)._labels
        except (TypeError, ValueError):
            return False
        
    def __getitem__(self, key, value):        
    
        if isinstance(key, int_types):
            
            if key < -len(self._labels) or key >= len(self._labels):
                raise IndexError("%s index (%d) out of range" % (self.nom, key) )
            item = self._labels[key]
        
        elif isinstance(key, str_types):
        
            try:
                item = self._label2index[key]
            except KeyError:
                raise KeyError("%s label (%s) not found" % (self.nom, repr(key) ) )
            
        elif isinstance(key, slice):
            
            slc = self._adapt_slice(key)
            item = tuple( self._labels[slc] )
            
        else:
            raise TypeError("invalid %s key (%s)" % (self.nom, repr(key)) )
    
        return item
    
    def __iadd__(self, other):
        raise TypeError("%s cannot be resized" % self.nom)
    
    def __add__(self, other):
        if not issubclass(type(other), TableLabels):
            other = self.__class__(other)
        return self.__class__(self._labels + other._labels)        
        
    def __iter__(self):
        for x in self._labels:
            yield x

    def __radd__(self, other):
        if not issubclass(type(other), TableLabels):
            other = self.__class__(other)
        return self.__class__(other._labels + self._labels)    

    def __len__(self):
        return len(self._labels)

    def __ne__(self, other):
        if isinstance(other, TableLabels):
            return self._labels != other._labels
        try:
            return self._labels != TableLabels(other)._labels
        except (TypeError, ValueError):
            return True

    def __nonzero__(self):
        return type(self).__bool__(self)

    def __reversed__(self):
        for x in reversed(self._labels):
            yield x 
    
    def __setitem__(self, key, value):
        
        if isinstance(key, int_types):
            
            self.set_label(key, value)
              
        elif isinstance(key, str_types):
            
            self.set_label(value, key)
            
        elif isinstance(key, slice):
            
            if not is_sized_iterable(labels) or isinstance(labels, str_types):
                raise TypeError("%s method takes a sized iterable of strings" % self.nom)

            slc = self._adapt_slice(key)
            
            slice_indices = [ i for i in range(slc.start, slc.stop, slc.step) ]
            
            if len(value) != len(slice_indices):
                raise TypeError("%s cannot be resized" % self.nom)
         
            for index, label in zip(slice_indices, value):
                self.set_label(index, label)
        else:
            raise TypeError("invalid %s key (%s)" % (self.nom, repr(key) ) )   
    
    def __str__(self):
        contents = "(%s)" % ", ".join( repr(x) for x in self._labels )
        return "%s%s" % (self.nom, contents)
  
    def _adapt_slice(self, slc):
        try:
            if not all( isinstance(x, tuple([int_types] + [NoneType]) ) 
                for x in (slc.start, slc.stop, slc.step) ):
                    raise TypeError("%s slice indices must be integer or None" % self.nom)
        except AttributeError:
            raise TypeError("%s _adapt_slice() takes a slice object" % self.nom)
    
        length = len(self._labels)
    
        if slc.step is None:
            step = 1
        elif slc.step != 0:
            step = slc.step
        else:
            raise ValueError("%s slice step cannot be zero" % self.nom)
 
        if slc.start is not None:
            start = slc.start
            if start < -length or start >= length:
                raise IndexError("%s slice start (%d) out of range" % (self.nom, start) )
            if start < 0:
                start += length
        else:
            start = 0 if step > 0 else length - 1

        if slc.stop is not None:
            stop = slc.stop
            if stop < -length or stop >= length:
                raise IndexError("%s slice stop (%d) out of range" % (self.nom, stop) )
            if stop < 0:
                stop += length
             
            if step == 1:
                if start > stop:
                    stop = start
            elif (step > 1 and start >= stop) or (step < 0 and start <= stop):
                raise ValueError("%s extended slice is of size 0" % self.nom)
        else:
            stop = length if step > 0 else -1

        return slice(start, stop, step)
  
    def append(self, value):
        raise TypeError("%s cannot be resized" % self.nom)
  
    def clear(self, key):
        
        if isinstance(key, int_types):
            
            if key < -len(self._labels) or key >= len(self._labels):
                raise IndexError("%s index (%d) out of range" % (self.nom, key) )
            
            self._labels[key] = ''
            del self._label2index[ self._labels[key] ]
              
        elif isinstance(key, str_types):
            
            if key not in self._label2index:
                raise KeyError("%s label (%s) not found" % (self.nom, repr(key)) )
            
            self._labels[ self._label2index[key] ] = ''
            del self._label2index[key]

        else:
            raise TypeError("invalid %s key (%s)" % (self.nom, repr(key) ) )

    def count(self, label):
        return 1 if label in self._label2index else 0 
  
    def extend(self, values):
        raise TypeError("%s cannot be resized" % self.nom)    
 
    def index(self, label):
        if label in self._label2index:
            return self._label2index[label]
        raise ValueError("%s label (%s) not found" % (self.nom, repr(key) ) )
 
    def insert(self, index, value):       
        raise TypeError("%s cannot be resized" % self.nom)  

    def pop(self):
        raise TypeError("%s cannot be resized" % self.nom)    

    def remove(self, label):
        raise TypeError("%s cannot be resized" % self.nom)

    def reverse(self):
        raise TypeError("%s cannot be reordered" % self.nom)

    def set_label(self, index, label):
        
        if not isinstance(index, int_types):
            raise TypeError("%s index (%s) must be an integer" % (self.nom, repr(index) ) )
        if index < -len(self._labels) or index >= len(self._labels):
            raise IndexError("%s index (%d) out of range" % (self.nom, index) )
        if index < 0:
            index += len(self._labels)
        if not isinstance(label, str_types) or label == '':
            raise TypeError("invalid %s label (%s)" % (self.nom, repr(label) ) )
        if label in self._label2index and index != self._label2index[label]:
            raise ValueError("%s cannot contain duplicate labels" % self.nom)
        
        if self._labels[index] in self._label2index:
            del self._label2index[ self._labels[index] ]
        
        self._labels[index] = label
        
        self._label2index[label] = index

    def tolist(self):
        return [ x for x in self._labels ]

class ListSlicer(object):

    @property
    def last(self):
        return self._last 

    @property
    def max(self):
        return self._max
 
    @property
    def min(self):
        return self._min
    
    @property
    def nom(self):
        return self.__class__.__name__
      
    @property
    def size(self):
        return self._size

    @property
    def slice(self):
        return slice(self._start, self._stop, self._step)

    @property
    def span(self):
        return self._span

    @property
    def start(self):
        return self._start

    @property
    def step(self):
        return self._step

    @property
    def stop(self):
        return self._stop

    def __init__(self, obj, key):
        
        if not isinstance(obj, BaseList):
            raise TypeError("%s() takes a BaseList object" % self.nom)
 
        if isinstance(key, int_types):
            
            index = obj._adapt_index(key)
            
            self._start = self._last = self._max = self._min = index
            self._stop = index + 1
            self._step = self._size = self._span = 1
            
        elif isinstance(key, slice):
            
            slc_info = dict()
            
            slc = obj._adapt_slice(key, slc_info)
            
            self._start = slc.start
            self._stop = slc.stop
            self._step = slc.step
            
            self._last = slc_info['last']
            self._max = slc_info['max'] 
            self._min = slc_info['min']
            self._size = slc_info['size']
            self._span = slc_info['span']
            
            self._rng = dict()
            
        else:
            raise TypeError("invalid %s index/key (%s)" % (obj.nom, repr(key) ) )

    def iter_decreasing(self):
        self._rng.setdefault('decreasing', tuple( 
          x for x in range(self._max, self._min - 1, -abs(self._step) ) ) )
        return self._rng['decreasing']

    def iter_increasing(self):
        self._rng.setdefault('increasing', tuple( 
          x for x in range(self._min, self._max + 1, abs(self._step) ) ) )
        return self._rng['increasing']

    def iter_indices(self):
        self._rng.setdefault('iter', tuple( 
          x for x in range(self._start, self._stop, self._step) ) )
        return self._rng['iter']

class TableSlicer(ListSlicer):

    @property
    def col_slice(self):
        return slice(self._start[1], self._stop[1], self._step[1])
        
    @property
    def row_slice(self):
        return slice(self._start[0], self._stop[0], self._step[0])

    @property
    def slice(self):
        raise NotImplementedError("%s has no property 'slice'" % self.nom)

    def __init__(self, table, row_key, col_key):
        
        if not isinstance(table, BaseTable):
            raise TypeError("%s() takes a BaseTable object" % self.nom)
        
        adapt_index = (table._adapt_index, table._adapt_index2)
        adapt_slice = (table._adapt_slice, table._adapt_slice2)
        
        start, step, stop, last, xmax, xmin, size, span,  = ( 
          [None] * 2 for _ in range(8) )
        
        for i, key in enumerate([row_key, col_key]):
            
            if isinstance(key, int_types):
                
                index = adapt_index[i](key)
                
                start[i] = last[i] = xmax[i] = xmin[i] = index
                stop[i] = index + 1
                step[i] = size[i] = span[i] = 1
                
            elif isinstance(key, slice):
            
                slc_info = dict()
                
                slc = adapt_slice[i](key, slc_info)
                    
                start[i] = slc.start
                stop[i] = slc.stop
                step[i] = slc.step
            
                last[i] = slc_info['last']
                xmax[i] = slc_info['max'] 
                xmin[i] = slc_info['min']
                size[i] = slc_info['size']
                span[i] = slc_info['span']
                
            else:
                raise TypeError("invalid %s index/key (%s)" % (table.nom, repr(key) ) )
        
        self._last = tuple(last)
        self._min = tuple(xmin)
        self._max = tuple(xmax)
        self._size = tuple(size)
        self._span = tuple(span)
        self._start = tuple(start)
        self._step = tuple(step)
        self._stop = tuple(stop)
        
        self._rng = ({}, {})
        
        self._row_lengths = dict()
        
        row_lengths = table.row_lengths
        
        if xmax[1] > table.min_row_length:
            for r in range(self._start[0], self._stop[0], self._step[0]):
                if row_lengths[r] <= self._max[1]:
                    self._row_lengths[r] = row_lengths[r]
    
    def iter_cols(self):
        self._rng[1].setdefault('iter', tuple( x for x in 
          range(self._start[1], self._stop[1], self._step[1]) ) )
        return self._rng[1]['iter']

    def iter_cols_decreasing(self):
        self._rng[1].setdefault('decreasing', tuple( x for x in 
          range(self._max[1], self._min[1] - 1, -abs(self._step[1]) ) ) )
        return self._rng[1]['decreasing']

    def iter_cols_increasing(self):
        self._rng[1].setdefault('increasing', tuple( x for x in 
          range(self._min[1], self._max[1] + 1, abs(self._step[1]) ) ) )
        return self._rng[1]['increasing']

    def iter_decreasing(self):
        for r in self.iter_rows_decreasing():
        
            for c in self.iter_cols_decreasing():
            
                if r in self._row_lengths and c >= self._row_lengths[r]:
                    yield None
                else:
                    yield (r, c)        

    def iter_increasing(self):
        for r in self.iter_rows_increasing():
        
            for c in self.iter_cols_increasing():
            
                if r in self._row_lengths and c >= self._row_lengths[r]:
                    yield None
                else:
                    yield (r, c)  

    def iter_indices(self):
        for r in self.iter_rows():
        
            for c in self.iter_cols():
            
                if r in self._row_lengths and c >= self._row_lengths[r]:
                    yield None
                else:
                    yield (r, c)

    def iter_rows(self):
        self._rng[0].setdefault('iter', tuple( x for x in 
          range(self._start[0], self._stop[0], self._step[0]) ) )
        return self._rng[0]['iter']

    def iter_rows_decreasing(self):
        self._rng[0].setdefault('decreasing', tuple( x for x in 
          range(self._max[0], self._min[0] - 1, -abs(self._step[0]) ) ) )
        return self._rng[0]['decreasing']

    def iter_rows_increasing(self):
        self._rng[0].setdefault('increasing', tuple( x for x in 
          range(self._min[0], self._max[0] + 1, abs(self._step[0]) ) ) )
        return self._rng[0]['increasing']

################################################################################