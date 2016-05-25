import os

def getIcon(name, type='.png'):
    file = os.path.join(os.path.dirname(__file__),'icons',name+type)
    if os.path.isfile(file):return file
    raise IOError('could not find icon '+name)
    
if __name__ == '__main__':
    print getIcon('3dsmax')