#!/usr/bin/python
# -*- coding: utf-8 -*-

from XiboMedia import XiboMedia
from threading import Thread

class ImageMedia(XiboMedia):
    def run(self):
	tmpXML = '<image href="data/130.png" id="M' + self.regionNodeNameExt + '" />'
	self.p.enqueue('add',(tmpXML,self.regionNodeName))
	self.p.enqueue('resize',('M' + self.regionNodeNameExt, self.width, self.height))
	self.p.enqueue('timer',(20000,self.parent.next))
