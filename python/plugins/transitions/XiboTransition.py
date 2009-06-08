#!/usr/bin/python
# -*- coding: utf-8 -*-

from threading import Thread

class XiboTransition(Thread):
    "Abstract Class - Interface for Transitions"
    def __init__(self,log,player,regionMgr,media1,media2):
	Thread.__init__(self)
	log.log(2,"info","Transition plugin loaded!")
	self.log = log
	self.regionMgr = regionMgr
	self.p = player
	self.media1 = media1
	self.media2 = media2

    def run(self):
	self.regionMgr.next()
