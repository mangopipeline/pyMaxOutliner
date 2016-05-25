import sys
dir = r'W:\publicRepositories'
if not dir in sys.path:sys.path.insert(0,dir)

import pyMaxOutliner as pyMO
reload(pyMO)

pyMO.run()