class Error(Exception):
   """Base class for other exceptions"""
   pass

class RedisHungError(Error):
    """Raised when the remote redis server is not responding to a ping request"""
    pass
