#!/usr/bin/python
# -*- coding: utf-8 -*-

from libavg import avg, anim
from xml.dom import minidom
import time, Queue

# Create an eventQueue to store events.
eventQueue = Queue.Queue(0)

# Create an array of active regions
regions = array()

Player = avg.Player()
Player.loadFile("assets/player.avg")
loadXlf("data/1.xlf")

# Functions to handle region/layout expirey
def loadXlf(xlfFile):
	global eventQueue
	global regions
	bg = Player.getElementByID("bg")

	dom = minidom.parse(xlfFile)
	
	layoutNode = dom.firstChild
	bgColor = layoutNode.attributes["bgcolor"]
	lWidth = layoutNode.attributes["width"]
	lHeight = layoutNode.attributes["height"]
	schemaVersion = layoutNode.attributes["schemaVersion"]
	
	for region in layoutNode.childNodes
		posX = region.attributes["left"]
		posY = region.attributes["top"]
		width = region.attributes["width"]
		height = region.attributes["height"]
		
		newXML = '<div id="region' . (len(regions) + 1) . '" x="' . posX  . '" y="' . posY . '" width="' . width . '" height="' . height  . '" opacity="' .  . '"></div>'
		newRegion = Player.createNode('newXML')
		bg.appendChild(newRegion)
		regions[len(regions)] = newRegion
		
		for media in region.childNodes
			pass

def nextEvent():
	step = eventQueue.get()

def nextMedia(m):
	pass

def expireRegion(r):
	pass

def expireLayout(l):
	pass

# Player.setInterval(1000, nextStep)
Player.play()
