#!/usr/bin/python
# -*- coding: utf-8 -*-

from XiboMedia import XiboMedia
from threading import Thread

class VideoMedia(XiboMedia):
    def run(self):
	tmpXML = '<video href="data/129.avi" id="' + self.mediaNodeName + '" />'
	self.p.enqueue('add',(tmpXML,self.regionNodeName))
	self.p.enqueue('play', self.mediaNodeName)
	self.p.enqueue('resize',(self.mediaNodeName, self.width, self.height))
	self.p.enqueue('timer',(20000,self.parent.next))
