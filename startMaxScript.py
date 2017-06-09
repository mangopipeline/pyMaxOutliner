import sys,time
devDir = r'C:\_otherDev' #change this part to match the folder contiant the pyMaxOutliner directory
if not dir in sys.path:sys.path.insert(0,devDir)

import pyMaxOutliner as pyMO
reload(pyMO)
print '-------------------'
print 'start loading pyMaxOutliner'
st = time.time()
ui = pyMO.run()
print ('Total Time Opening pyMaxOutliner %s seconds' % (time.time()-st))
