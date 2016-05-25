

'''
Created on May 24, 2016

@author: carlos
'''
from helpers import PySideUic,maxNode,iconLib
from PySide import QtGui, QtCore

import pymxs,MaxPlus,models
import os,time

reload(maxNode)
reload(models)

base,form = PySideUic.loadUiType(os.path.join(os.path.dirname(__file__),'views','main.ui'))
class mainApp(base,form):
    def __init__(self,parent=None):
        super(mainApp,self).__init__(parent)
        self.setupUi(self)
        self.mxs = pymxs.runtime
        self.setupTree()
        self.setupEvents()
    
    def selChanged(self,sel,dsel):
        select = [self._treeProxy.mapToSource(s).internalPointer()._data for s in sel.indexes()] 
        deselect = [self._treeProxy.mapToSource(s).internalPointer()._data for s in dsel.indexes()]
        self.mxs.deselect(deselect)
        self.mxs.selectMore(select)
            
    
    def treeRCMenu(self,x):
        qMenu = QtGui.QMenu(self)
        props = QtGui.QAction(self)
        props.setText('Properties')
        icon = iconLib.getIcon('settings')
        props.setIcon(QtGui.QIcon(icon))
        props.triggered.connect(lambda:QtGui.QMessageBox.about(self,'','place holder'))
        qMenu.addAction(props)
        qMenu.exec_(self.treeView.mapToGlobal(x))

        '''
        selMod = tv.selectionModel()
        sel = selMod.currentIndex()
        sel = tv.model().mapToSource(sel).internalPointer()
        data = sel.data()
        
        if (type(data) == vTDB.projects):
            qMenu = QtGui.QMenu(self)
            props = QtGui.QAction(self)
            props.setText('Properties')
            icon = iconLib.getIcon('settings')
            props.setIcon(QtGui.QIcon(icon))
            props.triggered.connect(lambda:self.runProjectSettings(data))
            qMenu.addAction(props)
            qMenu.exec_(tv.mapToGlobal(p))
        '''
    
    def setupEvents(self):
        self.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(lambda x : self.treeRCMenu(x))
        
        selMod = self.treeView.selectionModel()
        selMod.selectionChanged.connect(self.selChanged)
        
        
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
    
    def setupTree(self):
        self._data = self.genSceneData()
        
        self._treeModel =  models.treeModel(self._data)
        
        self._treeProxy = QtGui.QSortFilterProxyModel()
        self._treeProxy.setSourceModel(self._treeModel)
        
        self.treeView.setSortingEnabled(True)
        self.treeView.sortByColumn(0,QtCore.Qt.AscendingOrder)
        
        self._treeProxy.setDynamicSortFilter(True)
        
        self._treeProxy.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self._treeProxy.setSortRole(self._treeModel.sortRole)
        self._treeProxy.setFilterRole(self._treeModel.filterRole)
        
        self.treeView.setModel(self._treeProxy)
        
        #
        self.treeView.setAlternatingRowColors(True)
        self.treeView.setAnimated(True)
        self.treeView.setDragEnabled(True);
        self.treeView.setAcceptDrops(True);
        self.treeView.setDropIndicatorShown(True);
        

def run():
    global pyMaxOutlinerUI
    pyMaxOutlinerUI = mainApp(parent=MaxPlus.GetQMaxWindow())
    pyMaxOutlinerUI.show()
    
if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    ui = mainApp()
    ui.show()
    sys.exit(app.exec_())