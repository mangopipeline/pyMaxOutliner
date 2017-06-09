'''
Created on Apr 4, 2017

@author: carlos
'''
import MaxPlus

def listCodes():
    count = 0
    codelookup = {}
    
    for name in dir(MaxPlus.NotificationCodes):
        if not name.startswith('_'):
            val = getattr(MaxPlus.NotificationCodes, name)
            # we want to avoid registering for
            #define NOTIFY_INTERNAL_USE_START        0x70000000
            if ((type(val) == int) and (val <= 0xFFFF)):
                print "Notification code ", name, " = ", val
                codelookup[val] = name
                count += 1
    
    print "Number Notifications registered: ", count

if __name__ == '__main__':
    listCodes()