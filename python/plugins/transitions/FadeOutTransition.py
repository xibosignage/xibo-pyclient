#!/usr/bin/python
# -*- coding: utf-8 -*-

from XiboTransition import XiboTransition
from threading import Thread, Semaphore

class FadeOutTransition(XiboTransition):

    def run(self):
	self.lock = Semaphore()
	self.lock.acquire()

	if self.media1 != None:
		if self.options1['transOutDuration'] > 0:
			self.outDuration = int(self.options1['transOutDuration'])
		else:
			self.outDuration = 1000

		self.p.enqueue('anim',('fadeOut',self.media1.getName(),self.outDuration))
		self.p.enqueue('timer',(self.outDuration,self.next))
		self.lock.acquire()

	if self.media2 != None:
		if self.options2['transInDuration'] > 0:
			self.inDuration = int(self.options2['transInDuration'])
		else:
			self.inDuration = 1000

		self.p.enqueue('anim',('fadeOut',self.media2.getName(),self.inDuration))
		self.p.enqueue('timer',(self.inDuration,self.next))
		self.lock.acquire()

	self.callback()		

    def next(self):
	self.lock.release()
