from PySide import QtGui,QtCore

class outlinerTreeView(QtGui.QTreeView):
    def __init__(self,parent=True):
        super(outlinerTreeView,self).__init__(parent)
        
        self.setSelectionMode(self.ExtendedSelection)
        
        self.setAlternatingRowColors(True)
        self.setAnimated(True)
        

        self.setDropIndicatorShown(True)
        self.setDragDropOverwriteMode(True)
    
    def mousePressEvent(self,event):
        self.setDragEnabled(False)
        self.setAcceptDrops(False)
        
        if event.button() == QtCore.Qt.MiddleButton:
            self.setDragEnabled(True)
            self.setAcceptDrops(True)
        
        super(outlinerTreeView,self).mousePressEvent(event)