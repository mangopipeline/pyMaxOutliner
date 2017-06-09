

'''
Created on May 24, 2016

@author: carlos
'''
import os,sys

sys.path.insert(0,os.path.join(os.path.dirname(__file__),'_resources'))

from helpers import PySideUic,iconLib
from Qt import QtWidgets,QtGui, QtCore

import time,widgets, MaxPlus,pymxs

reload(PySideUic)
reload(widgets)

base,form = PySideUic.loadUiType(os.path.join(os.path.dirname(__file__),'views','main.ui'))
class mainApp(base,form):
    def __init__(self,parent=None):
        super(mainApp,self).__init__(parent)
        self.setupUi(self)
        self._mxs = pymxs.runtime
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
        qMenu = QtWidgets.QMenu(self)
        props = QtWidgets.QAction(self)
        props.setText('Properties')
        icon = iconLib.getIcon('settings')
        props.setIcon(QtWidgets.QIcon(icon))
        props.triggered.connect(lambda:QtWidgets.QMessageBox.about(self,'','place holder'))
        qMenu.addAction(props)
        qMenu.exec_(self.treeView.mapToGlobal(x))
    
    def setupEvents(self):
        self.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(lambda x : self.treeRCMenu(x))
    
    def closeEvent(self,event):
        self.treeView.killCallbacks()

def getMainWindow():
    try:
        return MaxPlus.GetQMaxWindow()
    except:
        return QtWidgets.QWidget(MaxPlus.GetQMaxMainWindow(), QtCore.Qt.Dialog)

def run():
    global pyMaxOutlinerUI
    pyMaxOutlinerUI = mainApp(parent=getMainWindow())
    st = time.time()
    pyMaxOutlinerUI.show()
    print ('show command took %s seconds' % (time.time()-st))
    return pyMaxOutlinerUI
    
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = mainApp()
    ui.show()
    sys.exit(app.exec_())