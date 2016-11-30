
from Qt import QtWidgets,QtGui,QtCore
import pymxs,sys,os,MaxPlus

#lets add this so we can import from the helpers package
homeDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if not homeDir in sys.path:sys.path.append(homeDir)


from helpers import iconLib, maxNode
import models

reload(maxNode)
reload(models)

class outlinerTreeView(QtWidgets.QTreeView):
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
        self._selMod = self.selectionModel()
        self.syncSelection()
        self.connectSignals()
        
        self.style()
        self.maxCallBacks()
        
    def setupModel(self):
        self._updateSel = True
        self._data = self.genSceneData()
        
        self._treeModel =  models.treeModel(self._data)
        
        self._treeProxy = QtWidgets.QSortFilterProxyModel()
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
        self._selMod.selectionChanged.connect(self.selChanged)
    
    def selChanged(self,sel,dsel):
        if not self._updateSel:return
        select = [self._treeProxy.mapToSource(s).internalPointer()._data for s in sel.indexes()] 
        deselect = [self._treeProxy.mapToSource(s).internalPointer()._data for s in dsel.indexes()]
        
        self._updateSel = False
        self.mxs.deselect(deselect)
        self.mxs.selectMore(select)
        self._updateSel = True
    
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
        #TODO: this logic needs to move to the model, and we we'll just ignore things that are allready parented..
        
        if dindex in indexes:return False #don't drop on selected nodes
        if not dindex.internalPointer():
            if all([(i.internalPointer()._data.parent != None) for i in indexes]):return True
            return False
        
        for i in indexes: #if the drop node is a child or grand child of any of the selected nodes don't allow...
            if dindex.internalPointer().isAncestor(i.internalPointer()):return False
        
        for i in indexes:
            if i.internalPointer() == dindex.internalPointer():return False
        
            
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
        self._updateSel = False
        #TODO: this might not be fireing becuse the model doesn't have MIMME types setup...
        model = self._treeProxy
        dindex = model.mapToSource(self.indexAt(event.pos()))
        sel = self.getDragNodes()
        
        if not self.isValidDrop(sel, dindex):
            event.ignore()
            return
        
        #at this point we let the model edit the data structure...

        self._treeModel.parentObjects(dindex, sel)
        self.syncSelection()
        event.accept()

        self._updateSel = True

    def syncSelection(self):
        import time
        self._updateSel = False
        st = time.time()
        sel = self._treeModel.getSelectedIndexs(self._treeProxy)
        print 'making q selection took ',(time.time()-st)
        st = time.time()
        self._selMod.clearSelection()
        self._selMod.select(sel, QtWidgets.QItemSelectionModel.Select)
        print 'applying bulk selection took',(time.time()-st)
        
        self._updateSel = True
    
    def MaxCBSelectionChanged(self,*args,**kwords):
        if not self._updateSel:return
        self.syncSelection()
        #print 'selection might have changed b'
        
    def maxCallBacks(self):
        #register upate callbacks...
        self._callBackIds = []
        codes = MaxPlus.NotificationCodes
        self._callBackIds.append(MaxPlus.NotificationManager.Register(codes.SelectionsetChanged,self.MaxCBSelectionChanged))
    
    def keyPressEvent(self,event):
        if event.key() == QtCore.Qt.Key_F:
            sel = self._selMod.selection().indexes()
            if not len(sel):return
            self.scrollTo(sel[0])
            print 'f'
            
    def killCallbacks(self):
        print 'destroy registered events'
        #Remove Call BAcks
        for cb in self._callBackIds: MaxPlus.NotificationManager.Unregister(cb)
