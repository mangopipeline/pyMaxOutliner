

'''
Created on May 24, 2016

@author: carlos
'''
from helpers import PySideUic,maxNode
from PySide import QtGui, QtCore

import pymxs,MaxPlus,models
import os

reload(maxNode)
reload(models)

base,form = PySideUic.loadUiType(os.path.join(os.path.dirname(__file__),'views','main.ui'))
class mainApp(base,form):
    def __init__(self,parent=None):
        super(mainApp,self).__init__(parent)
        self.setupUi(self)
        self.mxs = pymxs.runtime
        self.setupTree()
        
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
                if c.parent:par = nodesList[str(self.mxs.GetHandleByAnim(c.parent))]
                nodesList[id] = maxNode.Node(c,parent=par)
                chL = list(c.children)
                #print par.children()
                
                if not len(chL):continue
                nChild += chL
                
                
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
        #self.treeView.setRootIsDecorated(True)
        self.treeView.setAlternatingRowColors(True)
        self.treeView.setAnimated(True)
        

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