#!/usr/bin/python

from xibo import XiboDisplayManager

class XiboClient:
	def __init__(self):
		self.dm = XiboDisplayManager()
	
	def play(self):
		self.dm.start()

# Main - create a XiboClient and run
xc = XiboClient()
xc.play(xc)

class XiboDisplayManager:
    def __init__(self):
        pass
    
class XiboDownloadManager:
    def __init__(self):
        pass

class XiboDownloadThread:
    def __init__(self):
        pass

class XiboLayout:
    def __init__(self):
        pass

class Xmds:
    def __init__(self):
        pass

class XiboLayoutManager:
    def __init__(self):
        pass

class XiboRegionManager:
    def __init__(self):
        pass

class XiboMediaInterface:
    pass

class XiboMedia:
    def __init(self):
        pass