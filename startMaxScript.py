import sys
dir = r'W:\publicRepositories' #change this part to match the folder contiant the pyMaxOutliner directory
if not dir in sys.path:sys.path.insert(0,dir)

import pyMaxOutliner as pyMO
reload(pyMO)

pyMO.run()