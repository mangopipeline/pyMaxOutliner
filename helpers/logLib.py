import logging,os,socket,datetime



def buildDestinationPath(destRoot):
    unc = destRoot[:2] == '\\\\'
    if unc:destRoot = destRoot[2:]
        
    dirAr = destRoot.split('\\')
    cPth = dirAr[0]+'\\'
    if unc:cPth = '\\\\'+cPth
        
    del dirAr[0]
        
    for d in dirAr:
        cPth = os.path.join(cPth,d)
        if not os.path.isdir(cPth):
            try:
                os.makedirs(cPth)
            except Exception,e:
                if not os.path.isdir(cPth):raise e
            #if not os.path.isdir(cPth):return

def genLogFile(name,path):
    return os.path.join(path,name+'.log')

def genLoger(name,path,level='DEBUG'):
    #TODO: add a mode (user, machine) option right now it will work in the machine level only
    logFile = genLogFile(name,path)
    print logFile
    
    
    logger = logging.getLogger(name)
    handler = logging.FileHandler(logFile)
    
    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    handler.setFormatter(logFormatter)
    
    logger.addHandler(handler)
    #logger.addHandler(console_handler)
    
    lv = logging.INFO
    if level.lower() == 'debug':lv = logging.DEBUG
    logger.setLevel(lv)

    return logger

if __name__ == '__main__':
    path = os.path.dirname(__file__)
    log = genLoger('test',path)
    log.debug('hello world')