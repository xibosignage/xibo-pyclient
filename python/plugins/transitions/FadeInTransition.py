#!/usr/bin/python
# -*- coding: utf-8 -*-

from XiboTransition import XiboTransition
from threading import Thread, Semaphore

class FadeInTransition(XiboTransition):
    "Abstract Class - Interface for Transitions"

    def run(self):
	self.lock = Semaphore()
	self.lock.acquire()

	if self.media1 != None:
		if self.media1.options['transOutDuration'] > 0:
			self.outDuration = int(self.media1.options['transOutDuration'])
		else:
			self.outDuration = 1000

		self.p.enqueue('setOpacity',(self.media1.mediaNodeName,0.0))
		self.p.enqueue('anim',('fadeIn',self.media1.mediaNodeName,self.outDuration))
		self.p.enqueue('timer',(self.outDuration,self.next))
		self.lock.acquire()

	if self.media2 != None:
		if self.media2.options['transInDuration'] > 0:
			self.inDuration = int(self.media2.options['transInDuration'])
		else:
			self.inDuration = 1000

		self.p.enqueue('setOpacity',(self.media2.mediaNodeName,0.0))
		self.p.enqueue('anim',('fadeIn',self.media2.mediaNodeName,self.inDuration))
		self.p.enqueue('timer',(self.inDuration,self.next))
		self.lock.acquire()

	self.regionMgr.next()		

    def next(self):
	self.lock.release()
