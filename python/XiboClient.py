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

class XiboLog:
    level=0
    def __init__(self,level): abstract
    def log(self,level,category,message): abstract
    def stat(self,type, message, layoutID, scheduleID, mediaID): abstract
    
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
        
        # Final job. Create a libavg player, load an empty avg file and play it.
        self.Player = avg.Player()
        self.Player.showCursor(0);
        #self.Player.loadString("<avg id=\"main\" width=\"800\" height=\"600\"><div id=\"bg\" width=\"800\" height=\"600\" x=\"0\" y=\"0\" opacity=\"1\"></div></avg>")
        self.Player.loadFile("player.avg")
        self.bg = self.Player.getElementByID("bg")
        
        # Call a next Layout event now...
        self.nextLayout()
        
        # Start libavg running...
        self.Player.play()
        # play() blocks until we quit.
    
    def nextLayout(self):
        # Deal with any existing LayoutManagers that might still be running
        ##if self.currentLM.isRunning == true:
        ##    self.currentLM.dispose()
        
        # New LayoutManager
        self.currentLM = XiboLayoutManager(self, self.Player, self.bg, self.scheduler.nextLayout())
        self.currentLM.start()
        

class XiboDownloadManager(Thread):
    def __init__(self):
        Thread.__init__(self)
    
    def run(self):
        pass

class XiboDownloadThread(Thread):
    def __init__(self):
        Thread.__init__(self)

class XiboLayout:
    def __init__(self,layoutID):
        self.layoutID = layoutID

class Xmds:
    def __init__(self):
        pass

class XiboLayoutManager(Thread):
    def __init__(self,parent,player,background,layout):
        self.p = player
        self.bg = background
        self.l = layout
        self.parent = parent
        Thread.__init__(self)
    
    def run(self):
        region1 = self.p.createNode('<div id="region1" x="30" y="30" width="300" height="30" opacity="1"><words id="ClashText" x="" y="" font="arial" text="Layout ID ' + str(self.l.layoutID) +'" /></div>')
        self.bg.appendChild(region1)
        time.sleep(10)
        self.bg.removeChild(0)
        parent.nextLayout()
    
    def dispose(self):
        pass

class XiboRegionManager(Thread):
    def __init__(self):
        Thread.__init__(self)

class XiboMediaInterface:
    pass

class XiboMedia(Thread):
    def __init__(self):
        Thread.__init__(self)

class XiboScheduler(Thread):
    "Abstract Class - Interface for Schedulers"
    def run(self): abstract
    def nextLayout(self): abstract
    def hasNext(self): abstract

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
            
        return layout
    
    def hasNext(self):
        "Return true if there are more layouts, otherwise false"
        return true

class XiboClient:
    "Main Xibo DisplayClient Class. May host many DisplayManager classes"

    def __init__(self):
        pass
        
    def play(self):
        global version
        print _("Xibo Client v") + version
        
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