'''
Created on Mar 13, 2013

This module defines a spatial representation for by-hand selected regions

@author: curiel
'''

from math import sqrt, pi
from string import Template
import xml.etree.ElementTree as ET

class RegularRegion(object):
    '''Region in image cartesian system'''
    
    def __init__(self, data_tuple, uid, reg_type='rectangle'):
        self.data_tuple = data_tuple
        self.starting_point = (data_tuple[0], data_tuple[1])
        self.reg_type = reg_type
        self.uid = uid
        
        if 'circle' == reg_type :
            # (x,y, radius)
            self.radius = data_tuple[2]
            self.area = pi * (self.radius**2)
            self.perimeter = pi*self.radius*2
        elif 'rectangle' == reg_type :
            # (x,y,width,height)
            self.width = data_tuple[2]
            self.height = data_tuple[3]
            self.opposite_point = (data_tuple[0] + data_tuple[2],
                                   data_tuple[1] + data_tuple[3],)
            
            self.size = (self.width, self.height)
            self.area = self.width * self.height
            self.perimeter = 2 * self.width + 2 * self.height
        else:
            raise TypeError("Invalid type")
    
    def __eq__(self, some_region):
        if some_region.reg_type == self.reg_type:
            if self.reg_type == 'circle':
                #two circles
                pass
            else:
                #two rectangles
                if some_region.area == self.area:
                    if some_region.starting_point == self.starting_point:
                        if some_region.opposite_point == self.opposite_point:
                            return True
        return False
        
    def has_point_inside(self, point):
        if self.reg_type == 'circle':
            a = self.starting_point[0] - point[0]
            b = self.starting_point[1] - point[1]
            distance_to_center = sqrt(a**2 + b**2)
            if distance_to_center > self.radius:
                return False
            else:
                return True
        elif self.reg_type == 'rectangle':
            farthest_x = self.width + self.starting_point[0]
            farthest_y = self.height + self.starting_point[1]
            x_limit = farthest_x - point[0]
            y_limit = farthest_y - point[1]
             
            if x_limit < 0 or y_limit < 0:
                # It goes beyond one or both farthest limits
                return False
            elif x_limit > self.width or y_limit > self.height:
                # It is behind one or both starting_point limits
                return False
            else:
                # Its inside
                return True
        else:
            raise TypeError("Invalid type")

    def overlaps_with(self, region):
        ''''''
        if region.reg_type == self.reg_type:
            if self.reg_type == 'circle':
                #two circles
                pass
            else:
               
                #two rectangles
                pass
        elif region.reg_type == 'circle':
            # I'm a rectangle 
            pass
        else:
            # I'm a circle
            pass
    
    def contains(self, region):
        ''''''
        if region.reg_type == self.reg_type:
            if self.reg_type == 'circle':
                #two circles
                pass
            else:
                #two rectangles
                if self.has_point_inside(region.starting_point):
                    if self.has_point_inside(region.opposite_point):
                        return True
        elif region.reg_type == 'circle':
            # I'm a rectangle 
            pass
        else:
            # I'm a circle
            pass       
        
        return False

class RegionTree(object):
    
    def __init__(self,region):
        ''''''
        self.region = region
        self.children = {}
        
        self.xml_main_template = Template("<?xml version=\"1.0\"?>\n<regions>$regions\n</regions>")
        
        xml_region_template = "\n\t<region name=\"$name\">"
        xml_region_template += "\n\t\t<data>$data_tuple</data>"
        xml_region_template += "\n\t\t<type>$type</type>"
        #xml_region_template += "\n\t\t<origin>$origin</origin>"
        xml_region_template += "$children_section"
        xml_region_template += "\n\t</region>"
        self.xml_region_template = Template(xml_region_template)
        
        xml_children_template = "\n\t\t<children>"
        xml_children_template += "$children"
        xml_children_template += "\n\t\t</children>"
        self.xml_children_template = Template(xml_children_template)
        
        xml_child_template = "\n\t\t\t<child name=\"$name\"/>"
        self.xml_child_template = Template(xml_child_template)
        
    def __getitem__(self, key):
        return self.children[key]
    
    def __str__(self):
        return self.print_tree(self, 0)

    def __eq__(self, some_node):
        if not isinstance(some_node, RegionTree):
            return False
        return self.region == some_node.region
    
    def print_tree(self, depth=0):
        print "    " * depth, str(self.uid)
        for key in self.children.keys():
            child = self.children[key]
            child.print_tree(depth+1)
            
    def xml_string(self, first_node=True):
        
        xml_children = ""
        subtree_regions = ""
        
        for key in self.children.keys():
            child = self.children[key]
            xml_children += self.xml_child_template.substitute(name=child.region.uid)
            subtree_regions += child.xml_string(False)

        if xml_children != "":
            xml_children = self.xml_children_template.substitute(children=xml_children)

        xml_region = self.xml_region_template.substitute(name=self.region.uid,
                                            data_tuple=self.region.data_tuple,
                                            type=self.region.reg_type,
#                                            origin=self.region.starting_point,
                                            children_section=xml_children)
        
        regions_body = xml_region + subtree_regions

        if first_node:
            return self.xml_main_template.substitute(regions=regions_body)
        else:
            return regions_body

    @property
    def weight(self):
        return self.region.area
    
    @property
    def uid(self):
        return self.region.uid
    
    @property
    def starting_point(self):
        return self.region.starting_point
    
    @property
    def opposite_point(self):
        return self.region.opposite_point
    
    def contains(self, region_node):
        if isinstance(region_node, tuple):
            return self.region.has_point_inside(region_node)
        return self.region.contains(region_node.region)
    
    def insert(self, new_region):
        ''''''
        sinked = False
        if isinstance(new_region, RegularRegion):
            new_region = RegionTree(new_region)
        elif not isinstance(new_region, RegionTree):
            raise TypeError("Not a valid tree node")

        if not self.contains(new_region):
            return False
        
        for key in self.children.keys():
            child = self.children[key]
            if child.contains(new_region):
                child.insert(new_region)
                sinked = True
            elif new_region.contains(child):
                new_region.children[child.uid] = child
                self.children[new_region.uid] = new_region
                del self.children[key]
        if not sinked:
            self.children[new_region.uid] = new_region
        return True
    
    def eliminate(self, some_region):
        ''''''
        if isinstance(some_region, RegularRegion):
            some_region = RegionTree(some_region)
        elif not isinstance(some_region, RegionTree):
            raise TypeError("Not a valid tree node")

        for key in self.children.keys():
            child = self.children[key]
            if child == some_region:
                self.children.update(child.children)
                del self.children[key]
                return True
            elif child.contains(some_region):
                child.eliminate(some_region)
        return False
            
    def search_point(self, point):
        ''''''
        if not isinstance(point, tuple) and len(point) != 2:
            raise TypeError("Not a valid point")

        if self.contains(point):
            results = [self.uid]
        else:
            results = []

        for key in self.children.keys():
            child = self.children[key]
            if child.contains(point):
                results += child.search_point(point)

        return results
    
    @classmethod
    def tree_from_xml(self, region_distribution_xml):
        region_tree = None
        region_stack = []
        
        tree = ET.parse(region_distribution_xml)
        root = tree.getroot()
        
        for child in root:
            uid = child.attrib['name']
            for grandchild in list(child):
                if grandchild.tag == 'data':
                    data_tuple = [int(x) for x in grandchild.text.replace("(","").replace(")","").split(",")]
                    data_tuple = tuple(data_tuple)
                elif grandchild.tag == 'type':
                    region_type = grandchild.text
#                            elif grandchild.tag == 'origin':
#                                starting_point = grandchild.text
                else:
                    pass

            region = RegularRegion(tuple(data_tuple),
                                   uid,
                                   region_type)
            
            if region_tree == None:
                region_tree = RegionTree(region)
            else:
                region_tree.insert(region)
                region_stack.append(region)
        return (region_tree, region_stack)

class RPlusTreeNode(object):
    '''An R+tree (2-dimensional implementation)'''
    
    def __init__(self, region):
        ''''''
        self.region = region
        self.disjoint_children = [] # Completely contained
        self.overlapping_children = [] # Not completely contained

    def insert(self, new_region):
        '''Insert new_region in subtree rooted in self'''
        
        if isinstance(new_region, RegularRegion):
            new_region = RPlusTreeNode(new_region)
        elif not isinstance(new_region, RPlusTreeNode):
            raise TypeError("Not a valid tree node")
        
        if self.contains(new_region):
            for child in self.disjoint_children:
                if child.contains(new_region):
                    child.insert(new_region)
                elif new_region.contains(child):
                    new_region.insert(child)
                    self.eliminate(child)
            self.disjoint_children.append(object)
        elif not self.overlaps(new_region):
            return
        else:
            for child in self.disjoint_children + self.overlapping_children:
                if child.overlaps(new_region):
                    child.overlapping_children.append(new_region)
                    new_region.overlapping_children.append(child)

    def eliminate(self, region):
        pass
    
    def query(self, location):
        if isinstance(location, RegularRegion):
            pass
        else:
            if len(location) == 2:
                pass

    def contains(self, region_node):
        return self.region.contains(region_node.region)
    
    def overlaps(self, region_node):
        return self.region.overlaps(region_node.region)