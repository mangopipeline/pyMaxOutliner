'''
Created on May 24, 2016

@author: carlos
'''
class Node(object):
    def __init__(self,data, parent=None):
        self._data = data
        self._parent = None
        self._children = []
        self.parent = parent
    
        
    @property
    def name(self):
        return self._data.name
    
    @name.setter
    def name(self,value):
        self._data.name = value

    @property
    def children(self):
        return self._children
    
    @children.setter
    def children(self,valList):
        for c in self._children:c.parent = None
        if not len(valList):return
        
        for c in valList:c.parent = self
    
    @children.deleter
    def children(self):
        raise IOError('property ".children" may not be set directly please please change via target objects .parent property')

    
    def __addChild(self,value):
        if value in self._children:return
        self._children = self._children+[value]
        
        
    def __removeChild(self,value):
        indx = self._children.index(value)
        del self._children[indx]
   
    @property
    def parent(self):
        return self._parent
    
    @parent.setter
    def parent(self,value):
        if value == self:raise IOError("can not parent node to it's self")
        if self._parent:self._parent.__removeChild(self)
        self._parent = value
        if not value:return
        value.__addChild(self)
        #self._data.parent = value
    
    @parent.deleter
    def parent(self):
        self.parent = None
    
    def row(self):
        if self.parent:
            return self.parent.children.index(self)
    

    def log(self, tabLevel=-1):

        output     = ""
        tabLevel += 1
        
        for i in range(tabLevel):
            output += "\t"
        
        output += "|------" + self._name + "\n"
        
        for child in self._children:
            output += child.log(tabLevel)
        
        tabLevel -= 1
        output += "\n"
        
        return output