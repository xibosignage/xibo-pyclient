#!/usr/bin/python
# -*- coding: utf-8 -*-

from threading import Thread

class XiboMedia(Thread):
    "Abstract Class - Interface for Media"
    def __init__(self,log,parent,player,mediaNode):
	Thread.__init__(self)
	log.log(2,"info","ImageMedia loaded!")
	self.log = log
	self.parent = parent
	self.p = player
	self.mediaNode = mediaNode
	self.regionNodeName = self.parent.regionNodeName
	self.regionNodeNameExt = self.parent.regionNodeNameExt
	self.width = self.parent.width
	self.height = self.parent.height
	self.mediaNodeNameExt = "-" + str(self.p.nextUniqueId())
	# TODO: Extract media id and insert
	self.mediaNodeName = 'M' + '12' + self.regionNodeNameExt + self.mediaNodeNameExt

    def run(self): abstract
