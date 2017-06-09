
from Qt import QtWidgets,QtGui,QtCore
import pymxs,sys,os,MaxPlus,time

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
        
        #works on pyside and pyside2
        try:
            proxyM = QtGui.QSortFilterProxyModel(self)
        except:
            proxyM = QtCore.QSortFilterProxyModel(self)
      
        self._treeProxy = proxyM
        self._treeProxy.setSourceModel(self._treeModel)
        
        self.setSortingEnabled(True)
        self.sortByColumn(0,QtCore.Qt.AscendingOrder)
        
        self._treeProxy.setDynamicSortFilter(True)
        
        self._treeProxy.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self._treeProxy.setSortRole(self._treeModel.sortRole)
        self._treeProxy.setFilterRole(self._treeModel.filterRole)
        
        st = time.time()
        #this part is kind of slow...
        self.setModel(self._treeProxy)
        print ('set model took %s seconds (not sure how to speed this up)' % (time.time()-st))
    
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
    
    def genHndl(self,obj):
        return str(self.mxs.GetHandleByAnim(obj))
    
    def genSceneData(self):
        st = time.time()
        rootNode = self.mxs.rootNode
        root = maxNode.Node(rootNode)
        childN = list(rootNode.children)
        nodesList = {}
        self._lookUp = nodesList#should help speed finding new or deleted nodes...
        
        while len(childN):
            nChild = []
            for c in childN:
                id = self.genHndl(c)
                par = root
                if c.parent:
                    pId =  self.genHndl(c.parent)
                    par = nodesList[pId]
                
                nodesList[id] = maxNode.Node(c,parent=par)
                chL =  list(c.children)
                if len(chL):nChild = nChild+chL
                
            childN = nChild
        
        print 'mapping scene data took %s' % (time.time()-st)
        return root
    
    def mousePressEvent(self,event):
        self.setDragEnabled(False)
        
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
        
        
        #TODO:this method can probably be revisted now that the on parent call back is implemenetd.
        #this way we just reparent and let the call handle the tree update, worth a try
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
        self._updateSel = False
        st = time.time()
        sel = self._treeModel.getSelectedIndexs(self._treeProxy)
        #print 'making q selection took ',(time.time()-st)
        st = time.time()
        self._selMod.clearSelection()
        try:
            selectFlag = QtGui.QItemSelectionModel.Select
        except:
            selectFlag = QtCore.QItemSelectionModel.Select
            
        self._selMod.select(sel, selectFlag)
        #print 'applying bulk selection took',(time.time()-st)
        
        self._updateSel = True
    
    def MaxCBSelectionChanged(self,*args,**kwords):
        if not self._updateSel:return
        self.syncSelection()
        #print 'selection might have changed b'
    
    def MaxCBNewParentChange(self,*args,**kwords):
        if not self._updateSel:return
        #check where the parenting changed
        for o in self.mxs.objects:
            id = self.genHndl(o)
            
            #when you create a node for some reason a parent changed is fired before a new node event is fired 
            #so we need to check if this is a new node an if it is exit out...
            if not id in self._lookUp:
                continue
            
            on = self._lookUp[id]
            
            #if no parent state matches let's jump out...
            if not o.parent and on.parent == self._data:continue
            
            #let's get the actual parent helper
            if o.parent == None:
                pon = self._data
            else:
                pId  = self.genHndl(o.parent)
                pon = self._lookUp[pId]
                #if no parent change be out
                if on.parent == pon:continue
            
            self._treeModel.parentNode(on, pon)
    
    def MaxCBNewNode(self,*args,**kwords):
        #collect scene objects and see if we have process them before...
        for a in self.mxs.objects:
            id = self.genHndl(a)
            if id in self._lookUp:continue
            
            nd = maxNode.Node(a)
            self._lookUp[id] = nd
            
            self._treeModel.insertNode(nd,parent=self._data)
        
    def maxCallBacks(self):
        #register upate callbacks...
        self._callBackIds = []
        codes = MaxPlus.NotificationCodes
        self._callBackIds.append(MaxPlus.NotificationManager.Register(codes.SelectionsetChanged,self.MaxCBSelectionChanged))
        self._callBackIds.append(MaxPlus.NotificationManager.Register(codes.SceneAddedNode,self.MaxCBNewNode))
        self._callBackIds.append(MaxPlus.NotificationManager.Register(codes.NodeUnlinked,self.MaxCBNewParentChange))
        self._callBackIds.append(MaxPlus.NotificationManager.Register(codes.NodeLinked,self.MaxCBNewParentChange))
        
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
