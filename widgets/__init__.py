
from PySide import QtGui,QtCore
import pymxs,sys,os

#lets add this so we can import from the helpers package
homeDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if not homeDir in sys.path:sys.path.append(homeDir)


from helpers import iconLib, maxNode
import models

reload(maxNode)
reload(models)

class outlinerTreeView(QtGui.QTreeView):
    def __init__(self,parent=True):
        super(outlinerTreeView,self).__init__(parent)
        self.mxs = pymxs.runtime
        
        self.setSelectionMode(self.ExtendedSelection)
        
        self.setAlternatingRowColors(True)
        self.setAnimated(True)
        
        self.setDragDropMode(self.InternalMove)
        self.setAcceptDrops(True)
        
        self.setDropIndicatorShown(True)
        self.setDragDropOverwriteMode(True)
        self.setupModel()
        self.connectSignals()
        self.style()
    
    
    def setupModel(self):
        self._data = self.genSceneData()
        
        self._treeModel =  models.treeModel(self._data)
        
        self._treeProxy = QtGui.QSortFilterProxyModel()
        self._treeProxy.setSourceModel(self._treeModel)
        
        self.setSortingEnabled(True)
        self.sortByColumn(0,QtCore.Qt.AscendingOrder)
        
        self._treeProxy.setDynamicSortFilter(True)
        
        self._treeProxy.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self._treeProxy.setSortRole(self._treeModel.sortRole)
        self._treeProxy.setFilterRole(self._treeModel.filterRole)
        
        self.setModel(self._treeProxy)
    
    def connectSignals(self):
        #TODO: might want to change this to emit a signal so the actual object selection can happen outisde... might be over kill tho
        selMod = self.selectionModel()
        selMod.selectionChanged.connect(self.selChanged)
    
    def selChanged(self,sel,dsel):
        select = [self._treeProxy.mapToSource(s).internalPointer()._data for s in sel.indexes()] 
        deselect = [self._treeProxy.mapToSource(s).internalPointer()._data for s in dsel.indexes()]
        self.mxs.deselect(deselect)
        self.mxs.selectMore(select)
    
    def genSceneData(self):
        rootNode = self.mxs.rootNode
        root = maxNode.Node(rootNode)
        childN = list(rootNode.children)
        nodesList = {}
        
        while len(childN):
            nChild = []
            for c in childN:
                id = str(self.mxs.GetHandleByAnim(c))
                par = root
                if c.parent:
                    pId =  str(self.mxs.GetHandleByAnim(c.parent))
                    par = nodesList[pId]
                
                nodesList[id] = maxNode.Node(c,parent=par)
                chL =  list(c.children)
                if len(chL):nChild = nChild+chL
                
            childN = nChild

        return root
    
    def mousePressEvent(self,event):
        self.setDragEnabled(False)
        #self.setAcceptDrops(False)
        
        if event.button() == QtCore.Qt.MiddleButton:
            self.setDragEnabled(True)

        
        super(outlinerTreeView,self).mousePressEvent(event)
    
    def getDragNodes(self):
        model = self._treeProxy
        selM = self.selectionModel()
        return set([model.mapToSource(i) for i in selM.selectedIndexes()])
        
    def isValidDrop(self,indexes,dindex):
        if dindex in indexes:return False #don't drop on selected nodes
        if not dindex.internalPointer():return True #if there's no node allow to drop in empty space to unparent
        for i in indexes: #if the drop node is a child or grand child of any of the selected nodes don't allow...
            if dindex.internalPointer().isAncestor(i.internalPointer()):return False
        
        return True
    
    def startDrag(self,event):
        #TODO:start our own drag event so we can control the shadow effect of the drag and drop...
        super(outlinerTreeView,self).startDrag(event)
    
    def dragMoveEvent(self,event):
        model = self._treeProxy
        dindex = model.mapToSource(self.indexAt(event.pos()))
        
        sel = self.getDragNodes()
        
        if not self.isValidDrop(sel, dindex):
            event.ignore()
            return
        
        self._treeModel
        event.accept()
        
    def dropEvent(self,event):
        #TODO: this might not be fireing becuse the model doesn't have MIMME types setup...
        model = self._treeProxy
        dindex = model.mapToSource(self.indexAt(event.pos()))
        sel = self.getDragNodes()
        
        if not self.isValidDrop(sel, dindex):
            event.ignore()
            return
        
        #at this point we let the model edit the data structure...
        self._treeModel.parentObjects(dindex, sel)
        event.accept()

