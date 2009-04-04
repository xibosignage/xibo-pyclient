#!/usr/bin/python
# -*- coding: utf-8 -*-

from libavg import avg, anim
from xml.dom import minidom
import time, Queue, ConfigParser
import os
import re
import time
import sys
from threading import Thread

version = "1.1.0"

class XiboLog:
    def log(self,level,category,message): abstract
    
    def stat(self,type, message, layoutID, scheduleID, mediaID): abstract
    
class XiboLogFile(XiboLog):
    def log(self,level, category, message):
        pass
    
    def stat(self,type, message, layoutID, scheduleID, mediaID):
        pass

class XiboLogScreen(XiboLog):
    def __init__(self):
        self.log(2,"info","XiboLogScreen logger started")
    
    def log(self, level, category, message):
        print "LOG: " + str(level) + " " + category + " " + message
    
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
    
    def run(ClientRef):
        log.log(2,"info","New DisplayManager started")
    
class XiboDownloadManager(Thread):
    def __init__(self):
        pass

class XiboDownloadThread(Thread):
    def __init__(self):
        pass

class XiboLayout:
    def __init__(self,layoutID):
        pass

class Xmds:
    def __init__(self):
        pass

class XiboLayoutManager(Thread):
    def __init__(self):
        pass

class XiboRegionManager(Thread):
    def __init__(self):
        pass

class XiboMediaInterface:
    pass

class XiboMedia(Thread):
    def __init__(self):
        pass

class XiboScheduler(Thread):
    "Abstract Class - Interface for Schedulers"
    
    def run(): abstract
    
    def nextLayout(): abstract
    
    def hasNext(): abstract

class DummyScheduler(XiboScheduler):
    "Dummy scheduler - returns a list of layouts in rotation forever"
    layoutList = ['1', '2', '3']
    layoutIndex = 0
    
    def __init__(self):
        pass
    
    def run(self):
        pass
    
    def nextLayout():
        "Return the next valid layout"
        
        layout = XiboLayout(self.layoutList[self.layoutIndex])
        self.layoutIndex = self.layoutIndex + 1

        if self.layoutIndex == len(self.layoutList):
            self.layoutIndex = 0
            
        return layout
    
    def hasNext():
        "Return true if there are more layouts, otherwise false"
        return true

class XiboClient:
    "Main Xibo DisplayClient Class. May host many DisplayManager classes"

    def __init__(self):
        pass
        
    def play(self):
        global version
        print "Xibo Client v" + version
        
        print "Reading default configuration"
        global config
        config = ConfigParser.ConfigParser()
        config.readfp(open('defaults.cfg'))
        
        print "Reading user configuration"
        config.read(['site.cfg', os.path.expanduser('~/.xibo')])
        
        print "Log Level is: " + config.get('Main','logLevel');
        print "Logging will be handled by: " + config.get('Main','logWriter')
        print "Switching to new logger"
        
        global log
        logWriter = config.get('Main','logWriter')
        log = eval(logWriter)()
        log.log(2,"info","Switched to new logger")
        
        self.dm = XiboDisplayManager()
        
        self.dm.run()

# Main - create a XiboClient and run
xc = XiboClient()
xc.play()