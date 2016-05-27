

'''
Created on May 24, 2016

@author: carlos
'''
from helpers import PySideUic,iconLib
from PySide import QtGui, QtCore

import os,time,widgets, MaxPlus


reload(PySideUic)
reload(widgets)

base,form = PySideUic.loadUiType(os.path.join(os.path.dirname(__file__),'views','main.ui'))
class mainApp(base,form):
    def __init__(self,parent=None):
        super(mainApp,self).__init__(parent)
        self.setupUi(self)
        self.treeView = widgets.outlinerTreeView(parent=parent)
        self.horizontalLayout_2.addWidget(self.treeView)
        self.setupEvents()
        self.style()
        
    def style(self):
        s = ('QTreeView::indicator {width:20px; height:20px;}'
             'QTreeView::indicator:checked {image: url(:/icons/helpers/iconLib/icons/visible.png);}'
             'QTreeView::indicator:unchecked {image: url(:/icons/helpers/iconLib/icons/hidden.png);}')
        
        self.treeView.setStyleSheet(s)
    
    def treeRCMenu(self,x):
        qMenu = QtGui.QMenu(self)
        props = QtGui.QAction(self)
        props.setText('Properties')
        icon = iconLib.getIcon('settings')
        props.setIcon(QtGui.QIcon(icon))
        props.triggered.connect(lambda:QtGui.QMessageBox.about(self,'','place holder'))
        qMenu.addAction(props)
        qMenu.exec_(self.treeView.mapToGlobal(x))
    
    def setupEvents(self):
        self.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(lambda x : self.treeRCMenu(x))
        
     


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