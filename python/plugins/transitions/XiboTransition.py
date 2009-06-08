#!/usr/bin/python
# -*- coding: utf-8 -*-

from threading import Thread

class XiboTransition(Thread):
    "Abstract Class - Interface for Transitions"
    def __init__(self,log,player,media1,media2,callback,options1=None,options2=None):
	Thread.__init__(self)
	log.log(2,"info",self.__class__.__name__ + " plugin loaded!")
	self.log = log
	self.p = player
	self.media1 = media1
	self.media2 = media2
	self.callback = callback
	self.options1 = options1
	self.options2 = options2

	# Set an options1 and options2 dictionary
	if self.options1 == None:
		try:
			self.options1 = self.media1.options
		except:
			self.options1 = None
	if self.options2 == None:
		try:
			self.options2 = self.media2.options
		except:
			self.options2 = None

    def run(self):
	callback()
