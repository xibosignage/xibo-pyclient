#!/usr/bin/python
# -*- coding: utf-8 -*-

from XiboMedia import XiboMedia
from threading import Thread

class ImageMedia(XiboMedia):
    def add(self):
	# TODO: Fix the hardcoded path data/
	tmpXML = '<image href="data/' + str(self.options['uri']) + '" id="' + self.mediaNodeName + '" />'
	self.p.enqueue('add',(tmpXML,self.regionNodeName))
	self.p.enqueue('resize',(self.mediaNodeName, self.width, self.height))

    def run(self):
	self.p.enqueue('timer',(int(self.duration) * 1000,self.parent.next))
