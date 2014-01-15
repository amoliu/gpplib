class Error(Exception):
    ''' Base class for exceptions in gpplib. '''
    pass

class DateRangeError(Error):
    ''' Exception raised for errors in a date range 
    
    Attributes:
        msg 
    '''
    def __init__(self,msg):
        self.msg = msg

