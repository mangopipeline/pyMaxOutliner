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
    
    def __init__(self,data,log,parent=None):
        super(treeModel,self).__init__(parent)
        self.log = log
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
        if node.isDeleted:return
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
    
    def parentObjects(self,parent,children,skiScnP=False):
        pIn = None
        if parent.isValid():pIn = parent.internalPointer()
        if not pIn:pIn = self._data
        
        destInt = len(pIn.children)
        
        for c in children:
            #print parent,'->',c
            pI = self.parent(c)
            cIn = c.internalPointer()
            
            self.log.debug('-->moveRows1 %s %s %s %s %s' % (pI,c.row(),c.row(),parent,destInt))
            
            self.beginMoveRows(pI,c.row(),c.row(),parent,destInt)
            cIn.parent = pIn
            self.endMoveRows()
            destInt += 1
    
    def parentNode(self,node,parent):
        if not parent:parent = self._data
        self.log.debug('parenting %s to %s' % (node._data,parent._data))
        
        pI = self.indexFromNode(parent)
        nI = self.indexFromNode(node)
        
        papa = self.parent(nI)
        
        dest = len(parent.children)
        
        self.beginMoveRows(papa,nI.row(),nI.row(),pI,dest)
        node.parent(parent)
        self.endMoveRows()
        
    def indexFromNode(self,nd):
        if not nd.parent:return QtCore.QModelIndex()
        row = nd.parent.children.index(nd)
        indx = self.createIndex(row,0,nd)
        
        return indx
    
    def removeRow(self,nd):
        self.log.debug('model will now try to remove the row')
        index = self.indexFromNode(nd)
        parent = self.indexFromNode(nd.parent)
        self.log.debug('found qindex and parent qindex')
        
        self.log.debug('moving children to root')
        
        newP = self.createIndex(-1,-1,self._data)
        ch = nd.children[:]
        destInt = len(self._data.children)
        
        self.log.debug('moving rows')
        self.beginMoveRows(index,0,len(ch),newP,destInt)
        self.log.debug('parenting children to root')
        for c in ch:c.parent = self._data
        self.endMoveRows()
        
        r = index.row()
        self.beginRemoveRows(parent,r,r)
        self.log.debug('removing maxObjHelper parent')
        nd.parent = None
        self.log.debug('deleting maxObjHelper')
        del nd
        self.endRemoveRows()
        self.log.debug('done with removeRow Method...')
    
    def insertNode(self,node,parent):
        if not parent:parent = self._data
        #print 'inserting',node,'on parent',parent
        pI = self.indexFromNode(parent)
        pos = len(parent.children)
        self.beginInsertRows(pI,pos,pos)
        node.parent = parent
        self.endInsertRows()
    
    def getSelectedIndexs(self,proxy):
        #pyside and pyside 2 compatible
        try:
            out = QtGui.QItemSelection()
        except:
            out = QtCore.QItemSelection()
            
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
                    out.select(mI,mI)#,QtGui.QItemSelectionModel.Select)
                    
                    
            chld = grandChild
        return out
