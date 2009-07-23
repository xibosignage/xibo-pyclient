#!/usr/bin/python
# -*- coding: utf-8 -*-

from XiboMedia import XiboMedia
from threading import Thread

class VideoMedia(XiboMedia):
    def add(self):
	# TODO: Fix the hardcoded path data/
	tmpXML = '<video href="data/' + str(self.options['uri']) + '" id="' + self.mediaNodeName + '" opacity="0" />'
	self.p.enqueue('add',(tmpXML,self.regionNodeName))

    def run(self):
	self.p.enqueue('play', self.mediaNodeName)
	self.p.enqueue('resize',(self.mediaNodeName, self.width, self.height))
	self.p.enqueue('setOpacity',(self.mediaNodeName,1))
	if int(self.duration) > 0:
		self.p.enqueue('timer',(int(self.duration) * 1000,self.parent.next))
	else:
		self.p.enqueue('eofCallback',(self.mediaNodeName,self.parent.next))

    def requiredFiles(self):
	# TODO: Fix the hardcoded path data/
	return ['data/' + str(self.options['uri'])]
