#!/usr/bin/python
# -*- coding: utf-8 -*-

from libavg import avg, anim
from xml.dom import minidom
import time, Queue, ConfigParser, gettext
import os
import re
import time
import sys
from threading import Thread

version = "1.1.0"
schemaVersion = 1

#### Abstract Classes
class XiboLog:
    level=0
    def __init__(self,level): abstract
    def log(self,level,category,message): abstract
    def stat(self,type, message, layoutID, scheduleID, mediaID): abstract

class XiboScheduler(Thread):
    "Abstract Class - Interface for Schedulers"
    def run(self): abstract
    def nextLayout(self): abstract
    def hasNext(self): abstract
#### Finish Abstract Classes

#### Log Classes
class XiboLogFile(XiboLog):
    def __init__(self,level):
        pass
        
    def log(self,level, category, message):
        pass
    
    def stat(self,type, message, layoutID, scheduleID, mediaID):
        pass

class XiboLogScreen(XiboLog):
    def __init__(self,level):
        # Make sure level is sane
        if level == "" or int(level) < 0:
            level=0
        self.level = int(level)
        
        self.log(2,"info",_("XiboLogScreen logger started at level ") + str(level))
    
    def log(self, severity, category, message):
        if self.level >= severity:
            print "LOG: " + str(severity) + " " + category + " " + message
    
    def stat(self, type, message, layoutID, scheduleID, mediaID=""):
        print "STAT: " + type + " " + message + " " + str(layoutID) + " " + str(scheduleID) + " " + str(mediaID)

class XiboLogXmds(XiboLog):
    def log(self,level, category, message):
        pass
    
    def stat(self,type, message, layoutID, scheduleID, mediaID):
        pass
#### Finish Log Classes

#### Download Manager        
class XiboDownloadManager(Thread):
    def __init__(self):
        log.log(3,"info",_("New XiboDownloadManager instance created."))
        Thread.__init__(self)
    
    def run(self):
        log.log(2,"info",_("New XiboDownloadManager instance started."))

class XiboDownloadThread(Thread):
    def __init__(self):
        Thread.__init__(self)
#### Finish Download Manager
        
#### Webservice
class Xmds:
    def __init__(self):
        pass
#### Finish Webservice

#### Layout/Region Management
class XiboLayoutManager(Thread):
    def __init__(self,parent,player,layout,zindex=0,opacity=1.0):
        log.log(3,"info",_("New XiboLayoutManager instance created."))
        self.p = player
        self.l = layout
	self.zindex = zindex
        self.parent = parent
	self.opacity = opacity
	self.regions = []
	self.layoutNodeName = None
	self.layoutNodeNameExt = "-" + str(self.p.nextUniqueId())
	self.layoutExpired = False
	self.isPlaying = False
        Thread.__init__(self)
    
    def run(self):
	self.isPlaying = True
        log.log(2,"info",_("XiboLayoutManager instance running."))
	
	# TODO: Remove this whole block of code when appropriate.
#       self.p.enqueue('add',('<div id="region" x="30" y="30" width="300" height="30"><words id="text1" opacity="0" font="arial" text="Layout ID' + self.l.layoutID + '" /></div>','bg'))
#	self.p.enqueue('anim',('fadeIn','text1',3000))
#       time.sleep(7)
#	self.p.enqueue('anim',('fadeOut','text1',3000))
#	time.sleep(3)
#	self.p.enqueue("del","region")	
#	self.p.enqueue("reset","")
#       self.parent.nextLayout()

	# Add a DIV to contain the whole layout (for transitioning whole layouts in to one another)
	# TODO: Take account of the zindex parameter for transitions. Should this layout sit on top or underneath?
	# Ensure that the layoutNodeName is unique on the player (incase we have to transition to ourself)
	self.layoutNodeName = 'layout' + str(self.l.layoutID) + self.layoutNodeNameExt

	# Create the XML that will render the layoutNode.
	tmpXML = '<div id="' + self.layoutNodeName + '" width="' + str(self.l.sWidth) + '" height="' + str(self.l.sHeight) + '" x="' + str(self.l.offsetX) + '" y="' + str(self.l.offsetY) + '" opacity="' + str(self.opacity) + '" />'
	self.p.enqueue('add',(tmpXML,'screen'))

	# TODO: Fix background colour
	# Add a ColorNode and maybe ImageNode to the layout div to draw the background
	# tmpXML = '<colornode fillcolor="' + self.l.backgroundColour + '" id="bgColor' + self.layoutNodeNameExt + '" />'
	# self.p.enqueue('add',(tmpXML,self.layoutNodeName))

	if self.l.backgroundImage != None:
		tmpXML = '<image href="' + config.get('Main','libraryDir') + os.sep + str(self.l.backgroundImage) + '" width="' + str(self.l.sWidth) + '" height="' + str(self.l.sHeight) + '" id="bg' + self.layoutNodeNameExt + '" />'
		self.p.enqueue('add',(tmpXML,self.layoutNodeName))

	# TODO: Remove ME
	#tmpXML = '<video href="data/129.avi" width="200" height="150" x="20" y="20" id="video' + self.layoutNodeNameExt + '" />'
	#self.p.enqueue('add',(tmpXML,self.layoutNodeName))
	#self.p.enqueue('play','video' + self.layoutNodeNameExt)
	#time.sleep(20)
	#self.p.enqueue('anim',('fadeOut',self.layoutNodeName,2000))
	#time.sleep(2)
	#self.parent.nextLayout()
	# TODO: End Remove ME

	# Break layout in to regions
	# Spawn a region manager for each region and then start them all running
	# Log each region in an array for checking later.
	for cn in self.l.children():
		log.log(1,"info","node")
		if cn.nodeType == cn.ELEMENT_NODE and cn.localName == "region":
			log.log(1,"info","Encountered region")
			# Create a new Region Manager Thread and kick it running.
			# Pass in cn since it contains the XML for the whole region
		        tmpRegion = XiboRegionManager(self, self.p, self.layoutNodeName, self.layoutNodeNameExt, cn)
		        log.log(2,"info",_("XiboLayoutManager: run() -> Starting new XiboRegionManager."))
		        tmpRegion.start()
			# Store a reference to the region so we can talk to it later
			self.regions.append(tmpRegion)
			
    
    def regionElapsed(self):
	log.log(2,"info",_("Region elapsed. Checking if layout has elapsed"))

	allExpired = True
	for i in self.regions:
		if i.regionExpired == False:
			log.log(3,"info",_("Region " + i.regionName + " has not expired. Waiting"))
			allExpired = False

	if allExpired:
		log.log(2,"info",_("All regions have expired. Marking layout as expired"))
		self.layoutExpired = True
		# TODO: Testing only - remove
		self.p.enqueue('anim',('fadeOut',self.layoutNodeName,2000))
		time.sleep(2)
		# END
		self.parent.nextLayout()

    def dispose(self):
        self.p.enqueue("reset","")

class XiboRegionManager(Thread):
    def __init__(self,parent,player,layoutNodeName,layoutNodeNameExt,cn):
        log.log(3,"info",_("New XiboRegionManager instance created."))
        Thread.__init__(self)
	self.p = player
	self.parent = parent
	self.regionNode = cn
	self.layoutNodeName = layoutNodeName
	self.layoutNodeNameExt = layoutNodeNameExt
	self.regionExpired = False
	self.regionNodeNameExt = "-" + str(self.p.nextUniqueId())
	self.regionNodeName = self.regionNode.attributes['id'].value + self.regionNodeNameExt
	self.width = int(self.regionNode.attributes['width'].value) * parent.l.scaleFactor
	self.height =  int(self.regionNode.attributes['height'].value) * parent.l.scaleFactor
	self.top = int(self.regionNode.attributes['top'].value) * parent.l.scaleFactor
	self.left = int(self.regionNode.attributes['left'].value) * parent.l.scaleFactor

    def run(self):
        log.log(3,"info",_("New XiboRegionManager instance running for region:") + self.regionNodeName)
	tmpXML = '<video href="data/129.avi" width="' + str(self.width) + '" height="' + str(self.height) + '" x="' + str(self.left) + '" y="' + str(self.top) + '" id="video' + self.regionNodeNameExt + '" />'
	self.p.enqueue('add',(tmpXML,self.layoutNodeName))
	self.p.enqueue('play','video' + self.regionNodeNameExt)
	time.sleep(20)
	self.regionExpired = True
	self.parent.regionElapsed()
	
#### Finish Layout/Region Managment

#### Media
class XiboMediaInterface:
    pass

class XiboMedia(Thread):
    def __init__(self):
        Thread.__init__(self)
#### Finish Media

#### Scheduler Classes
class XiboLayout:
    def __init__(self,layoutID):
        self.layoutID = layoutID
	self.builtWithNoXLF = False
	self.schedule = ""
	self.layoutNode = None
	self.iter = None

	self.playerWidth = int(config.get('Main','width'))
	self.playerHeight = int(config.get('Main','height'))
	
	# Attributes
	self.width = None
	self.height = None
	self.sWidth = None
	self.sHeight = None
	self.offsetX = 0
	self.offsetY = 0
	self.scaleFactor = 1
	self.backgroundImage = None
	self.backgroundColour = None

	# Checks
	self.schemaCheck = False
	self.mediaCheck = False

	# Read XLF from file (if it exists)
	# Set builtWithNoXLF = True if it doesn't
	try:
		log.log(3,"info",_("Loading layout ID") + " " + self.layoutID + " " + _("from file") + " " + config.get('Main','libraryDir') + os.sep + self.layoutID + '.xlf')
		self.doc = minidom.parse(config.get('Main','libraryDir') + os.sep + self.layoutID + '.xlf')

		# Find the layout node and store it
		for e in self.doc.childNodes:
			if e.nodeType == e.ELEMENT_NODE and e.localName == "layout":
				self.layoutNode = e

		# Check the layout's schemaVersion matches the version this client understands
		try:
			xlfSchemaVersion = int(self.layoutNode.attributes['schemaVersion'].value)
		except KeyError:
			log.log(1,"error",_("Layout has no schemaVersion attribute and cannot be shown by this client"))
			self.schemaCheck = False
			return			

		if xlfSchemaVersion != schemaVersion:
			# Layout has incorrect schemaVersion.
			# Set the flag so the scheduler doesn't present this to the display
			log.log(1,"error",_("Layout has incorrect schemaVersion attribute and cannot be shown by this client.") + " " + str(xlfSchemaVersion) + " != " + str(schemaVersion))
			self.schemaCheck = False
			return
		else:
			self.schemaCheck = True

		# Setup variables from the layout node
		try:
			self.width = int(self.layoutNode.attributes['width'].value)
			self.height = int(self.layoutNode.attributes['height'].value)
			self.backgroundColour = str(self.layoutNode.attributes['bgcolor'].value)[1:]
		except KeyError:
			# Layout invalid as a required key was not present
			log.log(1,"error",_("Layout XLF is invalid. Missing required attributes"))

		try:
			self.backgroundImage = self.layoutNode.attributes['background'].value
		except KeyError:
			# Optional attributes, so pass on error.
			pass

		# Work out layout scaling and offset and set appropriate variables
		self.scaleFactor = min((self.playerWidth / float(self.width)),(self.playerHeight / float(self.height)))
		self.sWidth = int(self.width * self.scaleFactor)
		self.sHeight = int(self.height * self.scaleFactor)
		self.offsetX = abs(self.playerWidth - self.sWidth) / 2
		self.offsetY = abs(self.playerHeight - self.sHeight) / 2

		log.log(5,"debug",_("Screen Dimensions:") + " " + str(self.playerWidth) + "x" + str(self.playerHeight))
		log.log(5,"debug",_("Layout Dimensions:") + " " + str(self.width) + "x" + str(self.height))
		log.log(5,"debug",_("Scaled Dimensions:") + " " + str(self.sWidth) + "x" + str(self.sHeight))
		log.log(5,"debug",_("Offset Dimensions:") + " " + str(self.offsetX) + "x" + str(self.offsetY))
		log.log(5,"debug",_("Scale Ratio:") + " " + str(self.scaleFactor))

		# Present the children of the layout node for further parsing
		self.iter = self.layoutNode.childNodes

	except IOError:
		# File doesn't exist. Keep the layout object for the
		# schedule information it may contain later.
		log.log(3,"info",_("File does not exist. Marking layout built without XLF file"))
		self.builtWithNoXLF = True

    def resetSchedule(self):
	pass

    def addSchedule(self,fromDt,toDt):
	pass

    def canRun(self):
	return True

    def children(self):
	return self.iter
        
class DummyScheduler(XiboScheduler):
    "Dummy scheduler - returns a list of layouts in rotation forever"
    layoutList = ['1', '2', '3']
    layoutIndex = 0
    
    def __init__(self):
        Thread.__init__(self)
    
    def run(self):
        pass
    
    def nextLayout(self):
        "Return the next valid layout"
        
        layout = XiboLayout(self.layoutList[self.layoutIndex])
        self.layoutIndex = self.layoutIndex + 1

        if self.layoutIndex == len(self.layoutList):
            self.layoutIndex = 0
        
        log.log(3,"info",_("DummyScheduler: nextLayout() -> ") + str(layout.layoutID))
        return layout
    
    def hasNext(self):
        "Return true if there are more layouts, otherwise false"
        log.log(3,"info",_("DummyScheduler: hasNext() -> true"))
        return True
#### Finish Scheduler Classes

class XiboDisplayManager:
    def __init__(self):
        pass
    
    def run(self):
        log.log(2,"info",_("New DisplayManager started"))
        
        # Load a DownloadManager and start it running in its own thread
        try:
            downloaderName = config.get('Main','downloader')
            self.downloader = eval(downloaderName)()
            self.downloader.start()
            log.log(2,"info",_("Loaded Download Manager ") + downloaderName)
        except ConfigParser.NoOptionError:
            log.log(0,"error",_("No DownloadManager specified in your configuration."))
            log.log(0,"error",_("Please check your Download Manager configuration."))
            exit(1)
        except:
            log.log(0,"error",downloaderName + _(" does not implement the methods required to be a Xibo DownloadManager or does not exist."))
            log.log(0,"error",_("Please check your Download Manager configuration."))
            exit(1)
        # End of DownloadManager init
        
        # Load a scheduler and start it running in its own thread
        try:
            schedulerName = config.get('Main','scheduler')
            self.scheduler = eval(schedulerName)()
            self.scheduler.start()
            log.log(2,"info",_("Loaded Scheduler ") + schedulerName)
        except ConfigParser.NoOptionError:
            log.log(0,"error",_("No Scheduler specified in your configuration"))
            log.log(0,"error",_("Please check your scheduler configuration."))
            exit(1)
        except:
            log.log(0,"error",schedulerName + _(" does not implement the methods required to be a Xibo Scheduler or does not exist."))
            log.log(0,"error",_("Please check your scheduler configuration."))
            exit(1)
        # End of scheduler init
        
        # Final job. Create a XiboPlayer and start it running.
        self.Player = XiboPlayer()
	self.Player.start()
        
        # Call a next Layout event now...
        self.nextLayout()
            
    def nextLayout(self):
	# TODO: Whole function is wrong. This is where layout transitions should be supported.
	# Needs careful consideration.

        # Deal with any existing LayoutManagers that might still be running
	try:        
		if self.currentLM.isRunning == True:
        	    self.currentLM.dispose()
	except:
		pass
	self.Player.enqueue("reset","")        

        # New LayoutManager
        self.currentLM = XiboLayoutManager(self, self.Player, self.scheduler.nextLayout())
        log.log(2,"info",_("XiboLayoutManager: nextLayout() -> Starting new XiboLayoutManager with layout ") + str(self.currentLM.l.layoutID))
        self.currentLM.start()

class XiboPlayer(Thread):
	"Class to handle libavg interactions"
	def __init__(self):
		Thread.__init__(self)
		self.q = Queue.Queue(0)
		self.uniqueId = 0

	def getDimensions(self):
		return (self.player.width, self.player.height)

	def getElementByID(self,id):
		return self.player.getElementByID(id)

	def nextUniqueId(self):
		# This is just to ensure there are never two identically named nodes on the
		# player at once.
		# When we hit 100 times, reset to 0 as those nodes should be long gone.
		if self.uniqueId > 100:
			self.uniqueId = 0

		self.uniqueId += 1
		return self.uniqueId

	def run(self):
		log.log(1,"info",_("New XiboPlayer running"))
		self.player = avg.Player()
		if config.get('Main','fullscreen') == "true":
			self.player.setResolution(True,int(config.get('Main','width')),int(config.get('Main','height')),int(config.get('Main','bpp')))
		else:
			self.player.setResolution(False,int(config.get('Main','width')),int(config.get('Main','height')),int(config.get('Main','bpp')))
		#self.player.loadPlugin("ColorNode")
		self.player.showCursor(0)
		self.player.loadString('<avg id="main" width="' + config.get('Main','width') + '" height="' + config.get('Main','height') + '"><div id="screen"></div></avg>')
		self.player.setOnFrameHandler(self.frameHandle)
		self.player.play()

	def enqueue(self,command,data):
		log.log(3,"info","Enqueue: " + str(command) + " " + str(data))
		self.q.put((command,data))
		log.log(3,"info",_("Queue length is now") + " " + str(self.q.qsize()))

	def frameHandle(self):
		"Called on each new libavg frame. Takes queued commands and executes them"
		try:
			result = self.q.get(False)
			cmd = result[0]
			data = result[1]
			if cmd == "add":
				newNode = self.player.createNode(data[0])
				parentNode = self.player.getElementByID(data[1])
				parentNode.appendChild(newNode)
				log.log(5,"debug","Added new node to " + str(data[1]))
			elif cmd == "del":
				currentNode = self.player.getElementByID(data)
				parentNode = currentNode.getParent()
				parentNode.removeChild(currentNode)
				log.log(5,"debug","Removed node " + str(data))
			elif cmd == "reset":
				parentNode = self.player.getElementByID("screen")
				numChildren = parentNode.getNumChildren()
				log.log(5,"debug","Reset. Node has " + str(numChildren) + " nodes")
				for i in range(0,numChildren):
					try:
						node = parentNode.getChild(i)
						parentNode.removeChild(node)
						log.log(5,"debug","Removed child node at position " + str(i))
					except:
						pass
			elif cmd == "anim":
				currentNode = self.player.getElementByID(data[1])
				if data[0] == "fadeIn":
					animation = anim.fadeIn(currentNode,data[2])
				if data[0] == "fadeOut":
					animation = anim.fadeOut(currentNode,data[2])
			elif cmd == "play":
				currentNode = self.player.getElementByID(data)
				currentNode.play()
			elif cmd == "pause":
				currentNode = self.player.getElementByID(data)
				currentNode.pause()
			elif cmd == "stop":
				currentNode = self.player.getElementByID(data)
				currentNode.stop()				
			self.q.task_done()
			# Call ourselves again to action any remaining queued items
			# This does not make an infinite loop since when all queued items are processed
			# A Queue.Empty exception is thrown and this whole block is skipped.
			self.frameHandle()
		except Queue.Empty:
			pass

class XiboClient:
    "Main Xibo DisplayClient Class. May (in time!) host many DisplayManager classes"

    def __init__(self):
        pass
        
    def play(self):
        global version
        print _("Xibo Client v") + version

	global schemaVersion
        
        print _("Reading default configuration")
        global config
        config = ConfigParser.ConfigParser()
        config.readfp(open('defaults.cfg'))
        
        print _("Reading user configuration")
        config.read(['site.cfg', os.path.expanduser('~/.xibo')])
        
        logLevel = config.get('Logging','logLevel');
        print _("Log Level is: ") + logLevel;
        print _("Logging will be handled by: ") + config.get('Logging','logWriter')
        print _("Switching to new logger")
        
        global log
        logWriter = config.get('Logging','logWriter')
        log = eval(logWriter)(logLevel)
        try:

            log.log(2,"info",_("Switched to new logger"))
        except:
            print logWriter + _(" does not implement the methods required to be a Xibo logWriter or does not exist.")
            print _("Please check your logWriter configuration.")
            exit(1)
        
        self.dm = XiboDisplayManager()
        
        self.dm.run()

# Main - create a XiboClient and run
gettext.install("messages", "locale")

xc = XiboClient()
xc.play()
