'''
Created on May 24, 2016

@author: carlos
'''
import sys,os,cPickle,time
from Qt import QtWidgets,QtGui, QtCore
#from PySide import QtGui, QtCore

helpDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if not helpDir in sys.path:sys.path.append(helpDir)
from helpers import iconLib 
from itertools import chain

class treeModel(QtCore.QAbstractItemModel):
    sortRole = QtCore.Qt.UserRole
    filterRole = QtCore.Qt.UserRole + 1
    matchRole = QtCore.Qt.UserRole + 2
    
    def __init__(self,data,parent=None):
        super(treeModel,self).__init__(parent)
        self._data = data
        self._columnNames = ['Node Name']
    
    def supportedDropActions(self):
        return QtCore.Qt.CopyAction | QtCore.Qt.MoveAction
    
    def flags(self, index):
        defaultFlags =  QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable
        
        if index.isValid():return QtCore.Qt.ItemIsDropEnabled | QtCore.Qt.ItemIsDragEnabled | defaultFlags
        
        return QtCore.Qt.ItemIsDropEnabled | defaultFlags
        
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
        
        if column == 0 and role == QtCore.Qt.CheckStateRole: 
            if node.isHidden:return QtCore.Qt.Unchecked
            return QtCore.Qt.Checked
        
        if role == QtCore.Qt.DecorationRole:
            icon = iconLib.getIcon(node.iconName())
            if icon:
                pixmap = QtGui.QPixmap(icon,'1')
                icon = QtGui.QIcon(pixmap)
                return icon
        
        if role in (QtCore.Qt.DisplayRole,self.sortRole,self.filterRole):
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
        
        if not parent:parent = self._data
        if parent == self._data:return QtCore.QModelIndex()
        
        return self.createIndex(parent.row(),0,parent)
        
    def index(self,row,column,parent):
        parentNode = self.getNode(parent)
        childItem = None
        
        if len(parentNode.children) > row:childItem = parentNode.children[row]

        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()
    
    def setData(self,index, data, role):
        if not index.isValid(): return False
        if role == QtCore.Qt.CheckStateRole:
            node = index.internalPointer()
            node.isHidden = not node.isHidden
            return True
        #role != QtCore.Qt.EditRole:return False

        
        return False
    
    def parentObjects(self,parent,children):
        pIn = None
        if parent.isValid():pIn = parent.internalPointer()
        if not pIn:pIn = self._data
        
        destInt = len(pIn.children)
        
        for c in children:
            pI = self.parent(c)
            cIn = c.internalPointer()

            self.beginMoveRows(pI,c.row(),c.row(),parent,destInt)

            cIn.parent = pIn
            
            self.endMoveRows()
            destInt += 1
    
    def insertRows(self,row, count, parent):
        pass
    
    def removeRows(self,row,count,index,parent):
        pass
    
    def moveRows(self,srcPar,sourceRow,count,newPar,desInt):
        pass
    
    def getSelectedIndexs(self,proxy):
        out = QtWidgets.QItemSelection()
        chld = [self.index(i,0,None) for i in xrange(len(self._data.children))]
        first = None
        last = None
        
        while len(chld):
            grandChild = []
            for c in chld:
                node = c.internalPointer()
                for i in  xrange(len(node.children)):
                    grandChild.append(self.index(i,0,c))
                
                if node.isSelected:
                    mI = proxy.mapFromSource(c)
                    out.merge(QtWidgets.QItemSelection(mI,mI),QtGui.QItemSelectionModel.Select)
                    
                    
            chld = grandChild
        return out
