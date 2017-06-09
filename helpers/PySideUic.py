
try:
    import pyside2uic as uic
except:
    import pysideuic as uic
	
import xml.etree.ElementTree as xml
from cStringIO import StringIO
#from PySide import QtGui, QtCore
#PySide2 complaint import
from mango.Qt import QtGui, QtCore, QtWidgets

def loadUiType(uiFile):
    """
    Pyside "loadUiType" command like PyQt4 has one, so we have to convert the 
    ui file to py code in-memory first and then execute it in a special frame
    to retrieve the form_class.
    """
    parsed = xml.parse(uiFile)
    widget_class = parsed.find('widget').get('class')
    form_class = parsed.find('class').text

    with open(uiFile, 'r') as f:
        o = StringIO()
        frame = {}

        uic.compileUi(f, o, indent=0)
        pyc = compile(o.getvalue(), '<string>', 'exec')
        exec pyc in frame

        # Fetch the base_class and form class based on their type
        # in the xml from designer
        form_class = frame['Ui_%s'%form_class]
        base_class = eval('QtWidgets.%s'%widget_class)

    return base_class, form_class