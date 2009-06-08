#!/usr/bin/python
# -*- coding: utf-8 -*-

from XiboMedia import XiboMedia
from threading import Thread

class TvMedia(XiboMedia):
    def run(self):
	# TODO:
	# Must check here for existance of the v4l device. Adding a camera node with a non-existant v4l device causes a
	# crash which cannot be caught by the play loop exception handling.
	tmpXML = '<camera device="' + str(self.options['device']) + '" source="' + str(self.options['driver']) + '" id="' + self.mediaNodeName + '" capturewidth="640" captureheight="480" pixelformat="YUYV422" framerate="30" />'
	self.p.enqueue('add',(tmpXML,self.regionNodeName))
	self.p.enqueue('play', self.mediaNodeName)
	self.p.enqueue('resize',(self.mediaNodeName, self.width, self.height))
	self.p.enqueue('timer',(int(self.duration) * 1000,self.parent.next))
