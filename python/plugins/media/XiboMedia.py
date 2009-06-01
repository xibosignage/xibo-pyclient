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
	self.mediaNodeName = None
	self.mediaType = None
	self.duration = None
	self.schemaVersion = None
	self.invalid = False
	self.options = {}
	self.rawNode = None
	self.optionsNode = None

	# Calculate the media ID name
	try:
		self.mediaNodeName = "M" + str(self.mediaNode.attributes['id'].value) + self.regionNodeNameExt + self.mediaNodeNameExt
	except KeyError:
		log.log(1,"error",_("Media XLF is invalid. Missing required id attribute"))
		self.mediaNodeName = "M-invalid-" + self.regionNodeNameExt + self.mediaNodeNameExt
		self.invalid = True
		return

	# Calculate the media type
	try:
		self.mediaType = str(self.mediaNode.attributes['type'].value)
	except KeyError:
		log.log(1,"error",_("Media XLF is invalid. Missing required type attribute"))
		self.invalid = True
		return

	# Calculate the media duration
	try:
		self.duration = str(self.mediaNode.attributes['duration'].value)
	except KeyError:
		log.log(1,"error",_("Media XLF is invalid. Missing required duration attribute"))
		self.invalid = True
		return
	
	# Find the options and raw nodes and assign them to self.rawNode and self.optionsNode
	for cn in self.mediaNode.childNodes:
		if cn.nodeType == cn.ELEMENT_NODE and cn.localName == "options":
			self.optionsNode = cn
		if cn.nodeType == cn.ELEMENT_NODE and cn.localName == "raw":
			self.rawNode = cn			

	# Parse the options block in to the self.options[] array:
	for cn in self.optionsNode.childNodes:
		if cn.localName != None:
			self.options[str(cn.localName)] = cn.childNodes[0].nodeValue
			log.log(5,"info","Media Options: " + str(cn.localName) + " -> " + str(cn.childNodes[0].nodeValue))

    def run(self):
	# If there was a problem initialising the media object, kill it off and go to the next media item
	if self.invalid == True:
		self.parent.next()
		return
