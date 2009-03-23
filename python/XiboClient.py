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

