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
        print _("Xibo Client v") + version
        
        print _("Reading default configuration")
        global config
        config = ConfigParser.ConfigParser()
        config.readfp(open('defaults.cfg'))
        
        print _("Reading user configuration")
        config.read(['site.cfg', os.path.expanduser('~/.xibo')])
        
        print _("Log Level is: ") + config.get('Logging','logLevel');
        print _("Logging will be handled by: ") + config.get('Logging','logWriter')
        print _("Switching to new logger")
        
        global log
        logWriter = config.get('Logging','logWriter')
        log = eval(logWriter)()
        
        try:
            log.log(2,"info",_("Switched to new logger"))
        except:
            print logWriter + _(" does not implement the methods required to be a Xibo logWriter or does not exist.")
            print _("Please check your logWriter configuration.")
        
        self.dm = XiboDisplayManager()
        
        self.dm.run()

# Main - create a XiboClient and run
gettext.install("messages", "locale")

xc = XiboClient()
xc.play()