'''
Created on May 24, 2016

@author: carlos
'''
import sys,os
from PySide import QtGui, QtCore

helpDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not helpDir in sys.path:sys.path.append(helpDir)
from helpers import iconLib 


class treeModel(QtCore.QAbstractItemModel):
    sortRole = QtCore.Qt.UserRole
    filterRole = QtCore.Qt.UserRole + 1
    matchRole = QtCore.Qt.UserRole + 2
    
    def __init__(self,data,parent=None):
        super(treeModel,self).__init__(parent)
        self._data = data
        self._columnNames = ['Node Name']
        
    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable #| QtCore.Qt.ItemIsEditable
    
    def getNode(self,index):
        if index == None:return self._data
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node
        return self._data
      
    def rowCount(self,parent):
        if not parent.isValid():
            parentNode = self._data
        else:
            parentNode = parent.internalPointer()

        return len(parentNode.children)
    
    def columnCount(self,parent):
        return len(self._columnNames)
    
    def data(self,index,role):
        if not index.isValid():return None
        
        node = index.internalPointer()
        column = index.column()
        row = index.row()
        
        
        if role == QtCore.Qt.DecorationRole:
            icon = iconLib.getIcon(node.iconName())
            if icon:
                pixmap = QtGui.QPixmap(icon,'1')
                icon = QtGui.QIcon(pixmap)
                return icon
        
        if role == QtCore.Qt.DisplayRole:#,self.sortRole,self.filterRole):
            return node.name

    def headerData(self,section,orientation,role):
        if role == QtCore.Qt.DisplayRole:return self._columnNames[section]

    def parent(self,index):
        node = index.internalPointer()
        parent = None
        try:
            parent = node.parent
        except:
            return None
        
        if not parent:
            parent = self._data
        
        if parent == self._data:
            return QtCore.QModelIndex()
        
        return self.createIndex(parent.row(),0,parent)
        
    def index(self,row,column,parent):
        parentNode = self.getNode(parent)

        childItem = parentNode.children[row]

        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()
        