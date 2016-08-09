'''
Created on May 24, 2016

@author: carlos
'''
import pymxs

class Node(object):
    def __init__(self,data, parent=None):
        self.mxs = pymxs.runtime
        self._data = data
        self._parent = None
        self._children = []
        self.parent = parent
        
        
    def iconName(self):
        spC = str(self.mxs.superClassOf(self._data))
        if spC == 'GeometryClass' and str(self.mxs.classOf(self._data)) == "BoneGeometry":
            return 'BoneGeometry'
        return spC
    
    def isAncestor(self,Node):
        tNode = self
        while tNode.parent:
            if tNode.parent == Node:return True
            tNode = tNode.parent
        return False
    
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
    def isHidden(self):
        return self._data.isHidden
    
    @isHidden.setter
    def isHidden(self,value):
        #self._data.isSelected = value
        if value:
            self.mxs.hide(self._data)
        else:
            self.mxs.unhide(self._data)
            
    @isHidden.deleter
    def isHidden(self):
        raise IOError('can not delete isSelected Property')
   
    @property
    def isSelected(self):
        return self._data.isSelected
    
    @isSelected.setter
    def isSelected(self,value):
        self._data.isSelected = value
    
    @isSelected.deleter
    def isSelected(self):
        raise IOError('can not delete isSelected Property')
   
   
    @property
    def parent(self):
        return self._parent
    
    @parent.setter
    def parent(self,value):
        if value == self:raise IOError("can not parent node to it's self")
        if self._parent:self._parent.__removeChild(self)
        self._parent = value
        
        if value:
            par = None
            if value._data != self.mxs.rootNode:par = value._data
            self._data.parent = par
            #print self._data,'---->',value._data
        
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
        
        output += "|------" + self.name + "\n"
        
        for child in self._children:
            output += child.log(tabLevel)
        
        tabLevel -= 1
        #output += "\n"
        
        return output
    '''
    def __repr__(self):
        return self.log()
    '''