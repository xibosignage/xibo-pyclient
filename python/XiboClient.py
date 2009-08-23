#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# Xibo - Digitial Signage - http://www.xibo.org.uk
# Copyright (C) 2009 Alex Harrington
#
# This file is part of Xibo.
#
# Xibo is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version. 
#
# Xibo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Xibo.  If not, see <http://www.gnu.org/licenses/>.
#

from libavg import avg, anim
from SOAPpy import WSDL
import SOAPpy.Types
import SOAPpy.Errors
import xml.parsers.expat
from xml.dom import minidom
import time
import uuid
import hashlib
import Queue
import ConfigParser
import gettext
import os
import re
import time
import datetime
import sys
import socket
import inspect
from collections import defaultdict
from threading import Thread, Semaphore
import threading
import gd

import serial


version = "1.1.0a2"
#TODO: Change to 2!
schemaVersion = 1

#### Abstract Classes
class XiboLog:
    "Abstract Class - Interface for Loggers"
    level=0
    def __init__(self,level): abstract
    def log(self,level,category,message): abstract
    def stat(self,statType, fromDT, toDT, tag, layoutID, scheduleID, mediaID): abstract
    def setXmds(self,xmds):
        pass
    def setupInfo(self,p):
        self.p = p
        # Populate the info screen
        # Background.
        tmpXML = '<image href="resources/bgcolour-ffffff.png" id="infoBG" opacity="0.75" width="400" height="300" />'
        self.p.enqueue('add',(tmpXML,'info'))
        
        # Logo + version bottom right
        tmpXML = '<image href="resources/logo.png" id="infoLOGO" opacity="1" width="50" height="18" x="345" y="276" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<words x="290" y="280" opacity="1" text="v' + version + '" font="Arial" color="000000" size="12" />'
        self.p.enqueue('add',(tmpXML,'info'))
        
        # Required Files Traffic Light
        tmpXML = '<image href="resources/dotgrey.png" id="infoRFGrey" opacity="1" width="20" height="20" x="5" y="275" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotred.png" id="infoRFRed" opacity="0" width="20" height="20" x="5" y="275" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotamber.png" id="infoRFAmber" opacity="0" width="20" height="20" x="5" y="275" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotgreen.png" id="infoRFGreen" opacity="0" width="20" height="20" x="5" y="275" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<words x="10" y="270" opacity="1" text="Required Files" font="Arial" color="000000" size="10" angle="-1.57079633" pivotx="0" pivoty="0"/>'
        self.p.enqueue('add',(tmpXML,'info'))
        
        # GetFile Traffic Light
        tmpXML = '<image href="resources/dotgrey.png" id="infoGFGrey" opacity="1" width="20" height="20" x="30" y="275" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotred.png" id="infoGFRed" opacity="0" width="20" height="20" x="30" y="275" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotamber.png" id="infoGFAmber" opacity="0" width="20" height="20" x="30" y="275" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotgreen.png" id="infoGFGreen" opacity="0" width="20" height="20" x="30" y="275" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<words x="35" y="270" opacity="1" text="Get File" font="Arial" color="000000" size="10" angle="-1.57079633" pivotx="0" pivoty="0"/>'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<words id="infoRunningDownloads" x="37" y="278" opacity="1" text="0" font="Arial" color="00000" size="10" />'
        self.p.enqueue('add',(tmpXML,'info'))
        
        # Schedule Traffic Light
        tmpXML = '<image href="resources/dotgrey.png" id="infoSGrey" opacity="1" width="20" height="20" x="55" y="275" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotred.png" id="infoSRed" opacity="0" width="20" height="20" x="55" y="275" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotamber.png" id="infoSAmber" opacity="0" width="20" height="20" x="55" y="275" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotgreen.png" id="infoSGreen" opacity="0" width="20" height="20" x="55" y="275" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<words x="60" y="270" opacity="1" text="Schedule" font="Arial" color="000000" size="10" angle="-1.57079633" pivotx="0" pivoty="0"/>'
        self.p.enqueue('add',(tmpXML,'info'))
        
        # RegisterDisplay Traffic Light
        tmpXML = '<image href="resources/dotgrey.png" id="infoRDGrey" opacity="1" width="20" height="20" x="80" y="275" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotred.png" id="infoRDRed" opacity="0" width="20" height="20" x="80" y="275" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotamber.png" id="infoRDAmber" opacity="0" width="20" height="20" x="80" y="275" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotgreen.png" id="infoRDGreen" opacity="0" width="20" height="20" x="80" y="275" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<words x="85" y="270" opacity="1" text="Register Display" font="Arial" color="000000" size="10" angle="-1.57079633" pivotx="0" pivoty="0"/>'
        self.p.enqueue('add',(tmpXML,'info'))
        
        # Logs Traffic Light
        tmpXML = '<image href="resources/dotgrey.png" id="infoLogGrey" opacity="1" width="20" height="20" x="105" y="275" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotred.png" id="infoLogRed" opacity="0" width="20" height="20" x="105" y="275" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotamber.png" id="infoLogAmber" opacity="0" width="20" height="20" x="105" y="275" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotgreen.png" id="infoLogGreen" opacity="0" width="20" height="20" x="105" y="275" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<words x="110" y="270" opacity="1" text="Log" font="Arial" color="000000" size="10" angle="-1.57079633" pivotx="0" pivoty="0"/>'
        self.p.enqueue('add',(tmpXML,'info'))
        
        # Stats Traffic Light
        tmpXML = '<image href="resources/dotgrey.png" id="infoStatGrey" opacity="1" width="20" height="20" x="130" y="275" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotred.png" id="infoStatRed" opacity="0" width="20" height="20" x="130" y="275" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotamber.png" id="infoStatAmber" opacity="0" width="20" height="20" x="130" y="275" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotgreen.png" id="infoStatGreen" opacity="0" width="20" height="20" x="130" y="275" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<words x="135" y="270" opacity="1" text="Stats" font="Arial" color="000000" size="10" angle="-1.57079633" pivotx="0" pivoty="0"/>'
        self.p.enqueue('add',(tmpXML,'info'))

        # Lift Traffic Lights
        tmpXML = '<image href="resources/dotgrey.png" id="infoLift1Grey" opacity="1" width="10" height="10" x="165" y="285" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotred.png" id="infoLift1Red" opacity="0" width="10" height="10" x="165" y="285" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotamber.png" id="infoLift1Amber" opacity="0" width="10" height="10" x="165" y="285" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotgreen.png" id="infoLift1Green" opacity="0" width="10" height="10" x="165" y="285" />'
        self.p.enqueue('add',(tmpXML,'info'))
        
        tmpXML = '<image href="resources/dotgrey.png" id="infoLift2Grey" opacity="1" width="10" height="10" x="180" y="285" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotred.png" id="infoLift2Red" opacity="0" width="10" height="10" x="180" y="285" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotamber.png" id="infoLift2Amber" opacity="0" width="10" height="10" x="180" y="285" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotgreen.png" id="infoLift2Green" opacity="0" width="10" height="10" x="180" y="285" />'
        self.p.enqueue('add',(tmpXML,'info'))
        
        tmpXML = '<image href="resources/dotgrey.png" id="infoLift3Grey" opacity="1" width="10" height="10" x="195" y="285" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotred.png" id="infoLift3Red" opacity="0" width="10" height="10" x="195" y="285" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotamber.p9ng" id="infoLift3Amber" opacity="0" width="10" height="10" x="195" y="285" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotgreen.png" id="infoLift3Green" opacity="0" width="10" height="10" x="195" y="285" />'
        self.p.enqueue('add',(tmpXML,'info'))

        tmpXML = '<image href="resources/dotgrey.png" id="infoLift4Grey" opacity="1" width="10" height="10" x="210" y="285" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotred.png" id="infoLift4Red" opacity="0" width="10" height="10" x="210" y="285" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotamber.png" id="infoLift4Amber" opacity="0" width="10" height="10" x="210" y="285" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotgreen.png" id="infoLift4Green" opacity="0" width="10" height="10" x="210" y="285" />'
        self.p.enqueue('add',(tmpXML,'info'))
        
        tmpXML = '<image href="resources/dotgrey.png" id="infoLift5Grey" opacity="1" width="10" height="10" x="225" y="285" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotred.png" id="infoLift5Red" opacity="0" width="10" height="10" x="225" y="285" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotamber.png" id="infoLift5Amber" opacity="0" width="10" height="10" x="225" y="285" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotgreen.png" id="infoLift5Green" opacity="0" width="10" height="10" x="225" y="285" />'
        self.p.enqueue('add',(tmpXML,'info'))
        
        tmpXML = '<image href="resources/dotgrey.png" id="infoLift6Grey" opacity="1" width="10" height="10" x="240" y="285" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotred.png" id="infoLift6Red" opacity="0" width="10" height="10" x="240" y="285" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotamber.png" id="infoLift6Amber" opacity="0" width="10" height="10" x="240" y="285" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotgreen.png" id="infoLift6Green" opacity="0" width="10" height="10" x="240" y="285" />'
        self.p.enqueue('add',(tmpXML,'info'))
        
        tmpXML = '<image href="resources/dotgrey.png" id="infoLift7Grey" opacity="1" width="10" height="10" x="255" y="285" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotred.png" id="infoLift7Red" opacity="0" width="10" height="10" x="255" y="285" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotamber.png" id="infoLift7Amber" opacity="0" width="10" height="10" x="255" y="285" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotgreen.png" id="infoLift7Green" opacity="0" width="10" height="10" x="255" y="285" />'
        self.p.enqueue('add',(tmpXML,'info'))
        
        tmpXML = '<image href="resources/dotgrey.png" id="infoLift8Grey" opacity="1" width="10" height="10" x="270" y="285" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotred.png" id="infoLift8Red" opacity="0" width="10" height="10" x="270" y="285" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotamber.png" id="infoLift8Amber" opacity="0" width="10" height="10" x="270" y="285" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<image href="resources/dotgreen.png" id="infoLift8Green" opacity="0" width="10" height="10" x="270" y="285" />'
        self.p.enqueue('add',(tmpXML,'info'))

        # Lift Tag
        tmpXML = '<words id="infoLiftTag" x="165" y="265" opacity="1" text="Current Tag: default" font="Arial" color="000000" size="11" />'
        self.p.enqueue('add',(tmpXML,'info'))
        
        # Schedule
        tmpXML = '<words x="5" y="40" opacity="1" text="Schedule" font="Arial" color="000000" size="14" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<words id="infoCurrentSchedule" x="5" y="55" opacity="1" text="" font="Arial" color="000000" size="11" parawidth="180" linespacing="10" alignment="left" />'
        self.p.enqueue('add',(tmpXML,'info'))
        
        # Now Playing
        tmpXML = '<words x="5" y="5" opacity="1" text="Now Playing" font="Arial" color="000000" size="14" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<words id="infoNowPlaying" x="5" y="20" opacity="1" text="" font="Arial" color="000000" size="11" />'
        self.p.enqueue('add',(tmpXML,'info'))
        
        # Media
        tmpXML = '<words x="205" y="5" opacity="1" text="Media" font="Arial" color="000000" size="14" />'
        self.p.enqueue('add',(tmpXML,'info'))
        tmpXML = '<words id="infoMedia" x="205" y="20" opacity="1" text="" font="Arial" color="000000" size="11" />'
        self.p.enqueue('add',(tmpXML,'info'))
    
    def lights(self,field,value):
        if value == "green":
            self.p.enqueue('setOpacity',("info" + field + "Green", 1))
            self.p.enqueue('setOpacity',("info" + field + "Grey", 0))
            self.p.enqueue('setOpacity',("info" + field + "Amber", 0))
            self.p.enqueue('setOpacity',("info" + field + "Red", 0))
        if value == "red":
            self.p.enqueue('setOpacity',("info" + field + "Green", 0))
            self.p.enqueue('setOpacity',("info" + field + "Grey", 0))
            self.p.enqueue('setOpacity',("info" + field + "Amber", 0))
            self.p.enqueue('setOpacity',("info" + field + "Red", 1))
        if value == "amber":
            self.p.enqueue('setOpacity',("info" + field + "Green", 0))
            self.p.enqueue('setOpacity',("info" + field + "Grey", 0))
            self.p.enqueue('setOpacity',("info" + field + "Amber", 1))
            self.p.enqueue('setOpacity',("info" + field + "Red", 0))
        if value == "grey":
            self.p.enqueue('setOpacity',("info" + field + "Green", 0))
            self.p.enqueue('setOpacity',("info" + field + "Grey", 1))
            self.p.enqueue('setOpacity',("info" + field + "Amber", 0))
            self.p.enqueue('setOpacity',("info" + field + "Red", 0))

    def updateSchedule(self,schedule):
        self.p.enqueue('del','infoCurrentSchedule')
        tmpXML = '<words id="infoCurrentSchedule" x="5" y="55" opacity="1" text="' + schedule + '" font="Arial" color="000000" size="11" parawidth="180" linespacing="10" alignment="left" />'
        self.p.enqueue('add',(tmpXML,'info'))

    def updateNowPlaying(self,now):
        self.p.enqueue('del','infoNowPlaying')
        tmpXML = '<words id="infoNowPlaying" x="5" y="20" opacity="1" text="' + now + '" font="Arial" color="000000" size="11" />'
        self.p.enqueue('add',(tmpXML,'info'))

    def updateMedia(self,media):
        self.p.enqueue('del','infoMedia')
        tmpXML = '<words id="infoMedia" x="205" y="20" opacity="1" font="Arial" color="000000" size="11" parawidth="180">' + media + '</words>'
        self.p.enqueue('add',(tmpXML,'info'))
    
    def updateRunningDownloads(self,num):
        self.p.enqueue('del','infoRunningDownloads')
        tmpXML = '<words id="infoRunningDownloads" x="37" y="278" opacity="1" text="' + str(num) + '" font="Arial" color="00000" size="10" />'
        self.p.enqueue('add',(tmpXML,'info'))
    
    def updateLift(self,tag):
        self.p.enqueue('del','infoLiftTag')
        tmpXML = '<words id="infoLiftTag" x="165" y="265" opacity="1" text="Current Tag: ' + tag + '" font="Arial" color="000000" size="11" />'
        self.p.enqueue('add',(tmpXML,'info'))

class XiboScheduler(Thread):
    "Abstract Class - Interface for Schedulers"
    def run(self): abstract
    def nextLayout(self): abstract
    def hasNext(self): abstract
#### Finish Abstract Classes

#### Log Classes
class XiboLogFile(XiboLog):
    "Xibo Logger - to file"
    def __init__(self,level):
        try:
            self.fh = open('run.log','w')
        except:
            print "Unable to open run.log for writing."
            
        # Make sure level is sane
        if level == "" or int(level) < 0:
            level=0
        self.level = int(level)

        self.log(2,"info",_("XiboLogFile logger started at level ") + str(level))

    def log(self, severity, category, message):
        if self.level >= severity:
            try:
                currFrame = inspect.currentframe().f_back
                inspArray = inspect.getframeinfo(currFrame)
                callingMethod = inspArray[2]
                callingLineNumber = inspArray[1]
                # TODO: Figure out how to get the class name too
                callingClass = ""
            finally:
                del currFrame
            
            function = callingClass + "." + callingMethod
            
            date = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
            self.fh.write("LOG: " + str(date) + " (" + str(function) + ":" + str(callingLineNumber) + ") " + str(severity) + " " + category + " " + message + "\n")
            self.fh.flush()

    def stat(self,statType, fromDT, toDT, tag, layoutID, scheduleID, mediaID):
        pass
  

class XiboLogScreen(XiboLog):
    "Xibo Logger - to screen"
    def __init__(self,level):
        # Make sure level is sane
        if level == "" or int(level) < 0:
            level=0
        self.level = int(level)

        self.log(2,"info",_("XiboLogScreen logger started at level ") + str(level))

    def log(self, severity, category, message):
        if self.level >= severity:
            print "LOG: " + str(severity) + " " + category + " " + message

    def stat(self, statType, fromDT, toDT, tag, layoutID, scheduleID, mediaID=""):
        print "STAT: " + statType + " " + tag + " " + str(layoutID) + " " + str(scheduleID) + " " + str(mediaID)

class XiboLogXmds(XiboLog):
    def __init__(self,level):
        # Make sure level is sane
        if level == "" or int(level) < 0:
            level=0
        self.level = int(level)
        self.logs = Queue.Queue(0)
        self.stats = Queue.Queue(0)
        
        # Find out if we're doing stats, and how big the queue should be...
        try:
            self.statsOn = config.get('Stats','collect')
        except ConfigParser.NoOptionError:
            self.statsOn = 'false'        
        
        try:
            self.statsQueueSize = config.get('Stats','queueSize')
        except ConfigParser.NoOptionError:
            self.statsQueueSize = '99'
            
        self.worker = XiboLogXmdsWorker(self.logs,self.stats,self.statsQueueSize)
        self.worker.start()
    
    # Fast non-blocking log and stat functions
    # Logs and Stats pushed in native format on to the queue.
    # A worker thread will then format the messages in to XML
    # ready for transmission to the server.
    
    def log(self, severity, category, message):
        
        if self.level >= severity:
            try:
                currFrame = inspect.currentframe().f_back
                inspArray = inspect.getframeinfo(currFrame)
                callingMethod = inspArray[2]
                callingLineNumber = inspArray[1]
                # TODO: Figure out how to get the class name too
                callingClass = ""
            finally:
                del currFrame
            
            function = callingClass + "." + callingMethod
            
            date = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
            self.logs.put((date,severity,category,function,callingLineNumber,message),False)

    def stat(self,statType, fromDT, toDT, tag, layoutID, scheduleID, mediaID):
        if self.statsOn:
            self.stats.put((statType,fromDT,toDT,tag,layoutID,scheduleID,mediaID),False)
        return
        
    def setXmds(self,xmds):
        self.worker.xmds = xmds

class XiboLogXmdsWorker(Thread):
    def __init__(self,logs,stats,statsQueueSize):
        Thread.__init__(self)
        self.xmds = None
        self.logs = logs
        self.stats = stats
        self.running = True

        self.statXml = minidom.Document()
        self.statsE = self.statXml.createElement("stat")
        self.statXml.appendChild(self.statsE)
        self.statsQueueSize = statsQueueSize

        self.logXml = minidom.Document()
        self.logE = self.logXml.createElement("log")
        self.logXml.appendChild(self.logE)
    
    def run(self):
        # Wait for XMDS to be initialised and available to us
        while self.xmds == None:
            time.sleep(5)
            
        while self.running:
            # Deal with logs:
            try:
                # Prepare logs to XML and store in self.logXml
                while True:
                    date, severity, category, function, lineNo, message = self.logs.get(False)
                    traceE = self.logXml.createElement("trace")
                    traceE.setAttribute("date",date)
                    traceE.setAttribute("category",category)
                    self.logE.appendChild(traceE)
                    
                    messageE = self.logXml.createElement("message")
                    messageTxt = self.logXml.createTextNode(message)
                    messageE.appendChild(messageTxt)
                    
                    scheduleE = self.logXml.createElement("scheduleid")
                    layoutE = self.logXml.createElement("layoutid")
                    mediaE = self.logXml.createElement("mediaid")
                    methodE = self.logXml.createElement("method")
                    methodTxt = self.logXml.createTextNode(function)
                    methodE.appendChild(methodTxt)
                    lineE = self.logXml.createElement("line")
                    lineTxt = self.logXml.createTextNode(str(lineNo))
                    lineE.appendChild(lineTxt)
                    
                    traceE.appendChild(messageE)
                    traceE.appendChild(scheduleE)
                    traceE.appendChild(layoutE)
                    traceE.appendChild(mediaE)
                    traceE.appendChild(methodE)
                    traceE.appendChild(lineE)
                    
            except Queue.Empty:
                # Exception thrown breaks the inner while loop
                # Do nothing
                pass
            
            try:
                # Ship the logXml off to XMDS
                self.xmds.SubmitLog(self.logXml.toxml())
                #print "LOGGING: " + self.logXml.toxml()
                
                # Reset logXml
                self.logXml = minidom.Document()
                self.logE = self.logXml.createElement("log")
                self.logXml.appendChild(self.logE)
                try:
                    os.remove(config.get('Main','libraryDir') + os.sep + 'log.xml')
                except:
                    pass
            except XMDSException:
                # Flush to disk incase we crash before getting another chance
                try:
                    try:
                        f = open(config.get('Main','libraryDir') + os.sep + 'log.xml','w')
                        f.write(self.logXml.toxml())
                    finally:
                        f.close()
                except:
                    pass
                
            # Deal with stats:
            if self.stats.qsize() >= self.statsQueueSize:
                try:
                    # Prepare stats to XML and store in self.statXml
                    while True:
                        statType, fromDT, toDT, tag, layoutID, scheduleID, mediaID = self.stats.get(False)
                        statE = self.statXml.createElement("stat")
                        statE.setAttribute("type",statType)
                        statE.setAttribute("fromdt",fromDT)
                        statE.setAttribute("todt",toDT)
                        
                        if statType == "event":
                            statE.setAttribute("tag",tag)
                        elif statType == "media":
                            statE.setAttribute("mediaid",mediaID)
                            statE.setAttribute("layoutid",layoutID)
                        elif statType == "layout":
                            statE.setAttribute("layoutid",layoutID)
                            statE.setAttribute("scheduleid",scheduleID)
                                                
                        self.statsE.appendChild(statE)
                                                
                except Queue.Empty:
                    # Exception thrown breaks the inner while loop
                    # Do nothing
                    pass
                
                try:
                    # Ship the statXml off to XMDS
                    self.xmds.SubmitStats(self.statXml.toxml())
                    
                    # Reset statXml
                    self.statXml = minidom.Document()
                    self.statsE = self.logXml.createElement("stats")
                    self.statXml.appendChild(self.statsE)
                    try:
                        os.remove(config.get('Main','libraryDir') + os.sep + 'stats.xml')
                    except:
                        pass
                except XMDSException:
                    # Flush to disk incase we crash before getting another chance
                    try:
                        try:
                            f = open(config.get('Main','libraryDir') + os.sep + 'stats.xml','w')
                            f.write(self.statXml.toxml())
                        finally:
                            f.close()
                    except:
                        pass
            
            time.sleep(30)
        
#### Finish Log Classes

#### Download Manager
class XiboFile(object):
    def __init__(self,path,targetHash):
        self.__path = path
        self.md5 = ""
        self.checkTime = 1
        self.update()
        self.targetHash = targetHash

    def update(self):
        # Generate MD5
        m = hashlib.md5()
        try:
            fd = open(self.__path,"rb")
        except IOError:
            return False
        content = fd.readlines()
        fd.close()
        for eachLine in content:
            m.update(eachLine)
        self.md5 = m.hexdigest()

        self.checkTime = time.time()
        return True

    def isExpired(self):
        if self.checkTime < time.time() + 3600:
            return False
        return True

    def isValid(self):
        return self.md5 == self.targetHash

class XiboDownloadManager(Thread):
    def __init__(self,xmds,player):
        Thread.__init__(self)
        log.log(3,"info",_("New XiboDownloadManager instance created."))
        self.xmds = xmds
        self.running = True
        self.dlQueue = Queue.Queue(0)
        self.p = player
        self.__lock = Semaphore()
        self.__lock.acquire()

        # Store a dictionary of XiboDownloadThread objects so we know
        # which files are downloading and how many download slots
        # there are free
        self.runningDownloads = defaultdict(XiboDownloadThread)

        # How many XiboDownloadThreads should run at once
        self.maxDownloads = 5

    def run(self):
        log.log(2,"info",_("New XiboDownloadManager instance started."))
        while (self.running):
            self.interval = 300

            # Find out how long we should wait between updates.
            try:
                self.interval = int(config.get('Main','xmdsUpdateInterval'))
            except:
                # self.interval has been set to a sensible default in this case.
                log.log(0,"warning",_("No XMDS Update Interval specified in your configuration"))
                log.log(0,"warning",_("Please check your xmdsUpdateInterval configuration option"))
                log.log(0,"warning",_("A default value has been used:") + " " + str(self.interval) + " " + _("seconds"))

            # Go through the list comparing required files to files we already have.
            # If a file differs, queue it for download
            reqFiles = '<files></files>'
            try:
                reqFiles = self.xmds.RequiredFiles()
                log.log(5,"info",_("XiboDownloadManager: XMDS RequiredFiles() returned ") + str(reqFiles))
                f = open(config.get('Main','libraryDir') + os.sep + 'rf.xml','w')
                f.write(reqFiles)
                f.close()
            except IOError:
                log.log(0,"error",_("Error trying to cache RequiredFiles to disk"))
            except XMDSException:
                log.log(0,"warning",_("XMDS RequiredFiles threw an exception"))
                try:
                    try:
                        f = open(config.get('Main','libraryDir') + os.sep + 'rf.xml')
                        reqFiles = f.read()
                    finally:
                        f.close()
                except:
                    # Couldn't read or file doesn't exist. Either way, return a blank list.
                    pass

            self.doc = None
            # Pull apart the retuned XML
            try:
                self.doc = minidom.parseString(reqFiles)
            except:
                log.log(0,"warning",_("XMDS RequiredFiles returned invalid XML"))

            # Find the layout node and store it
            if self.doc != None:
                for e in self.doc.childNodes:
                    if e.nodeType == e.ELEMENT_NODE and e.localName == "files":
                        # e is a files node.
                        #log.log(5,"info","Files Node found!")
                        for f in e.childNodes:
                            # It's a Media node
                            if f.nodeType == f.ELEMENT_NODE and f.localName == "file" and str(f.attributes['type'].value) == "media":
                                #log.log(5,"info","Media File Node found!")
                                # Does the file exist? Is it the right size?
                                try:
                                    tmpPath = config.get('Main','libraryDir') + os.sep + str(f.attributes['path'].value)
                                    tmpSize = int(f.attributes['size'].value)
                                    tmpHash = str(f.attributes['md5'].value)
                                    tmpType = str(f.attributes['type'].value)
                                    self.updateInfo()
                                    if os.path.isfile(tmpPath) and os.path.getsize(tmpPath) == tmpSize:
                                        # File exists and is the right size
                                        # See if we checksummed it recently
                                        if tmpPath in md5Cache:
                                            # Check if the md5 cache is old for this file
                                            if md5Cache[tmpPath].isExpired():
                                                # Update the cache if it is
                                                md5Cache[tmpPath].update()

                                            if not md5Cache[tmpPath].isValid():
                                                # The hashes don't match.
                                                # Queue for download.
                                                log.log(2,"warning",_("File exists and is the correct size, but the checksum is incorrect. Queueing for download. ") + tmpPath)
                                                self.dlQueue.put((tmpType,tmpPath,tmpSize,tmpHash),False)
                                        else:
                                            tmpFile = XiboFile(tmpPath,tmpHash)
                                            md5Cache[tmpPath] = tmpFile
                                            if not tmpFile.isValid():
                                                # The hashes don't match.
                                                # Queue for download.
                                                log.log(2,"warning",_("File exists and is the correct size, but the checksum is incorrect. Queueing for download. ") + tmpPath)
                                                self.dlQueue.put((tmpType,tmpPath,tmpSize,tmpHash),False)
                                    else:
                                        # Queue the file for download later.
                                        log.log(3,"info",_("File does not exist or is not the correct size. Queueing for download. ") + tmpPath)
                                        self.dlQueue.put((tmpType,tmpPath,tmpSize,tmpHash),False)
                                except:
                                    # TODO: Blacklist the media item.
                                    log.log(0,"error",_("RequiredFiles XML error: File type=media has no path attribute or no size attribute. Blacklisting."))
                                log.log(5,"audit",_("File " + tmpPath + " is valid."))

                            # It's a Layout node.
                            if f.nodeType == f.ELEMENT_NODE and f.localName == "file" and str(f.attributes['type'].value) == "layout":
                                try:
                                    tmpPath = config.get('Main','libraryDir') + os.sep + str(f.attributes['path'].value) + '.xlf'
                                    tmpHash = str(f.attributes['md5'].value)
                                    tmpType = str(f.attributes['type'].value)
                                    self.updateInfo()
                                    if os.path.isfile(tmpPath):
                                        # File exists
                                        # See if we checksummed it recently
                                        if tmpPath in md5Cache:
                                            # Check if the md5 cache is old for this file
                                            if md5Cache[tmpPath].isExpired():
                                                # Update the cache if it is
                                                md5Cache[tmpPath].update()
                                            
                                            # The file is in cache, but has changed hash on the server
                                            if md5Cache[tmpPath].targetHash != tmpHash:
                                                md5Cache[tmpPath].targetHash = tmpHash
                                                md5Cache[tmpPath].update()

                                            if md5Cache[tmpPath].md5 != tmpHash:
                                                # The hashes don't match.
                                                # Queue for download.
                                                log.log(2,"warning",_("File exists and is the correct size, but the checksum is incorrect. Queueing for download. ") + tmpPath)
                                                self.dlQueue.put((tmpType,tmpPath,0,tmpHash),False)
                                        else:
                                            tmpFile = XiboFile(tmpPath,tmpHash)
                                            md5Cache[tmpPath] = tmpFile
                                            if not tmpFile.isValid():
                                                # The hashes don't match.
                                                # Queue for download.
                                                log.log(2,"warning",_("File exists and is the correct size, but the checksum is incorrect. Queueing for download. ") + tmpPath)
                                                self.dlQueue.put((tmpType,tmpPath,0,tmpHash),False)
                                    else:
                                        # Queue the file for download later.
                                        log.log(3,"info",_("File does not exist. Queueing for download. ") + tmpPath)
                                        self.dlQueue.put((tmpType,tmpPath,0,tmpHash),False)
                                except:
                                    # TODO: Blacklist the media item.
                                    log.log(0,"error",_("RequiredFiles XML error: File type=layout has no path attribute or no hash attribute. Blacklisting."))

                            # It's a Blacklist node
                            if f.nodeType == f.ELEMENT_NODE and f.localName == "file" and str(f.attributes['type'].value) == "blacklist":
                                #log.log(5,"info","Blacklist File Node found!")
                                # TODO: Do something with the blacklist
                                pass
            # End If self.doc != None

            # Loop over the queue and download as required
            try:
                # Throttle this to a maximum number of dl threads.
                while True:
                    tmpType, tmpPath, tmpSize, tmpHash = self.dlQueue.get(False)

                    # Check if the file is downloading already
                    if not tmpPath in self.runningDownloads:
                        # Make a download thread and actually download the file.
                        # Add the running thread to the self.runningDownloads dictionary
                        self.runningDownloads[tmpPath] = XiboDownloadThread(self,tmpType,tmpPath,tmpSize,tmpHash)
                        self.runningDownloads[tmpPath].start()
                        log.updateRunningDownloads(len(self.runningDownloads))

                    while len(self.runningDownloads) >= (self.maxDownloads - 1):
                        # There are no download thread slots free
                        # Sleep for 5 seconds and try again.
                        log.log(3,"info",_("All download slots filled. Waiting for a download slot to become free"))
                        time.sleep(5)
                    # End While

            except Queue.Empty:
                # Used to exit the above while once all items are downloaded.
                pass

            # Loop over the MD5 hash cache and remove any entries older than 1 hour
            # TODO: Throws an exception "ValueError: too many values to unpack"
            for tmpPath, tmpFile in md5Cache.iteritems():
                if tmpFile.isExpired():
                    del md5Cache[tmpPath]
            # End Loop

            # Update the infoscreen.
            self.updateInfo()
            
            log.log(5,"audit",_("There are ") + str(threading.activeCount()) + _(" running threads."))
            log.log(3,"audit",_("XiboDownloadManager: Sleeping") + " " + str(self.interval) + " " + _("seconds"))
            self.p.enqueue('timer',(int(self.interval) * 1000,self.collect))
            self.__lock.acquire()
        # End While
    
    def collect(self):
        self.__lock.release()

    def dlThreadCompleteNotify(self,tmpPath):
        # Download thread completed. Log and remove from
        # self.runningDownloads
        log.log(3,"info",_("Download thread completed for ") + tmpPath)
        del self.runningDownloads[tmpPath]
        log.updateRunningDownloads(len(self.runningDownloads))

    def updateInfo(self):
        # Update the info screen with information about the media
        # and it's status
        infoStr = ""
        
        for tmpPath, tmpFile in md5Cache.iteritems():
            if tmpFile.isValid():
                infoStr += tmpPath + ", "
            else:
                infoStr += "<i>" + tmpPath + "</i>, "
        
        log.updateMedia(infoStr)

class XiboDownloadThread(Thread):
    def __init__(self,parent,tmpType,tmpPath,tmpSize,tmpHash):
        Thread.__init__(self)
        self.tmpType = tmpType
        self.tmpPath = tmpPath
        self.tmpSize = tmpSize
        self.tmpHash = tmpHash
        self.parent = parent
        self.offset = 0
        self.chunk = 512000

    def run(self):
        # Manage downloading the appropriate type of file:
        if self.tmpType == "media":
            self.downloadMedia()
        elif self.tmpType == "layout":
            self.downloadLayout()

        # Let the DownloadManager know we're complete
        self.parent.dlThreadCompleteNotify(self.tmpPath)

    def downloadMedia(self):
        # Actually download the Media file
        finished = False
        tries = 0

        if os.path.isfile(self.tmpPath):
            try:
                os.remove(self.tmpPath)
            except:
                log.log(0,"error",_("Unable to delete file: ") + self.tmpPath)
                return

        fh = None
        try:
            fh = open(self.tmpPath, 'wb')
        except:
            log.log(0,"error",_("Unable to write file: ") + self.tmpPath)
            return

        while tries < 5 and not finished:
            tries = tries + 1
            failCounter = 0
            while self.offset < self.tmpSize and failCounter < 3:
                # If downloading this chunk will complete the file
                # work out exactly how much to download this time
                if self.offset + self.chunk > self.tmpSize:
                    self.chunk = self.tmpSize - self.offset

                try:
                    # Fix path attribute so it's just the filename (minus the client path)
                    shortPath = self.tmpPath.replace(config.get('Main','libraryDir') + os.sep,'',1)
                    response = self.parent.xmds.GetFile(shortPath,self.tmpType,self.offset,self.chunk)
                    fh.write(response)
                    fh.flush()
                    self.offset = self.offset + self.chunk
                    failCounter = 0
                except RuntimeError:
                    # TODO: Do something sensible
                    pass
                except XMDSException:
                    # TODO: Do something sensible
                    failCounter = failCounter + 1

            # End while offset<tmpSize
            try:
                fh.close()
            except:
                # TODO: Do something sensible
                pass

            # Check size/md5 here?
            tmpFile = XiboFile(self.tmpPath,self.tmpHash)
            if tmpFile.isValid():
                finished = True
                md5Cache[self.tmpPath] = tmpFile
        # End while

    def downloadLayout(self):
        # Actually download the Layout file
        finished = False
        tries = 0

        if os.path.isfile(self.tmpPath):
            try:
                os.remove(self.tmpPath)
            except:
                log.log(0,"error",_("Unable to delete file: ") + self.tmpPath)
                return

        fh = None
        try:
            fh = open(self.tmpPath, 'wb')
        except:
            log.log(0,"error",_("Unable to write file: ") + self.tmpPath)
            return

        while tries < 5 and not finished:
            tries = tries + 1

            try:
                # Fix path attribute so it's just the filename (minus the client path) and trailing .xlf
                shortPath = self.tmpPath.replace(config.get('Main','libraryDir') + os.sep,'',1)
                shortPath = self.tmpPath.replace('.xlf','',1)

                response = self.parent.xmds.GetFile(shortPath,self.tmpType,0,0)
                fh.write(response + '\n')
                fh.flush()
            except RuntimeError:
                # TODO: Do something sensible
                pass
            except XMDSException:
                # TODO: Do we need to do anything here?
                pass

            try:
                fh.close()
            except:
                # TODO: Do something sensible
                pass

            # TODO: Should we check size/md5 here?
            finished = True
        # End while

#### Finish Download Manager

#### Layout/Region Management
class XiboLayoutManager(Thread):
    def __init__(self,parent,player,layout,zindex=0,opacity=1.0,hold=False):
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
        self.hold = hold
        self.__regionLock = Semaphore()
        self.__regionDisposeLock = Semaphore()
        self.expiring = False
        self.nextLayoutTriggered = False
        Thread.__init__(self)

    def run(self):
        self.isPlaying = True
        log.log(2,"info",_("XiboLayoutManager instance running."))

        # Add a DIV to contain the whole layout (for transitioning whole layouts in to one another)
        # TODO: Take account of the zindex parameter for transitions. Should this layout sit on top or underneath?
        # Ensure that the layoutNodeName is unique on the player (incase we have to transition to ourself)
        self.layoutNodeName = 'L' + str(self.l.layoutID) + self.layoutNodeNameExt

        # Create the XML that will render the layoutNode.
        tmpXML = '<div id="' + self.layoutNodeName + '" width="' + str(self.l.sWidth) + '" height="' + str(self.l.sHeight) + '" x="' + str(self.l.offsetX) + '" y="' + str(self.l.offsetY) + '" opacity="' + str(self.opacity) + '" />'
        self.p.enqueue('add',(tmpXML,'screen'))

        # TODO: Fix background colour
        # Add a ColorNode and maybe ImageNode to the layout div to draw the background

        # This code will work with libavg > 0.8.x
        # tmpXML = '<colornode fillcolor="' + self.l.backgroundColour + '" id="bgColor' + self.layoutNodeNameExt + '" />'
        # self.p.enqueue('add',(tmpXML,self.layoutNodeName))
        if self.l.backgroundColour != None:
            if not os.path.isfile(config.get('Main','libraryDir') + os.sep + 'bgcolour-' + self.l.backgroundColour + '.png'):
                im = gd.image((1,1))
                try:
                    color = im.colorAllocate(self.HTMLColorToRGB(self.l.backgroundColour))
                except ValueError:
                    log.log(3,"error",_("Layout background colour is not a valid HTML Hex Colour string. Using black instead."))
                    color = im.colorAllocate((255,255,255))
                
                im.rectangle((0,0),(1,1),color)
                im.writePng(config.get('Main','libraryDir') + os.sep + 'bgcolour-' + self.l.backgroundColour + '.png')
            
            tmpXML = '<image href="' + config.get('Main','libraryDir') + os.sep + 'bgcolour-' + str(self.l.backgroundColour) + '.png" width="' + str(self.l.sWidth) + '" height="' + str(self.l.sHeight) + '" id="bgColor' + self.layoutNodeNameExt + '" />'
            self.p.enqueue('add',(tmpXML,self.layoutNodeName))

        if self.l.backgroundImage != None:
            tmpXML = '<image href="' + config.get('Main','libraryDir') + os.sep + str(self.l.backgroundImage) + '" width="' + str(self.l.sWidth) + '" height="' + str(self.l.sHeight) + '" id="bg' + self.layoutNodeNameExt + '" />'
            self.p.enqueue('add',(tmpXML,self.layoutNodeName))

        # Break layout in to regions
        # Spawn a region manager for each region and then start them all running
        # Log each region in an array for checking later.
        for cn in self.l.children():
            if cn.nodeType == cn.ELEMENT_NODE and cn.localName == "region":
                # Create a new Region Manager Thread and kick it running.
                # Pass in cn since it contains the XML for the whole region
                tmpRegion = XiboRegionManager(self, self.p, self.layoutNodeName, self.layoutNodeNameExt, cn)
                log.log(2,"info",_("XiboLayoutManager: run() -> Starting new XiboRegionManager."))
                # TODO: Instead of starting here, we need to sort the regions array by zindex attribute
                # then start in ascending order to ensure rendering happens in layers correctly.
                tmpRegion.start()
                # Store a reference to the region so we can talk to it later
                self.regions.append(tmpRegion)

    # From ActivState Recipies: http://code.activestate.com/recipes/266466/
    def HTMLColorToRGB(self,colorstring):
        """ convert #RRGGBB to an (R, G, B) tuple """
        colorstring = colorstring.strip()
        if colorstring[0] == '#': colorstring = colorstring[1:]
        if len(colorstring) != 6:
            raise ValueError, "input #%s is not in #RRGGBB format" % colorstring
        r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:]
        r, g, b = [int(n, 16) for n in (r, g, b)]
        return (r, g, b)

    def regionElapsed(self):
        log.log(2,"info",_("Region elapsed. Checking if layout has elapsed"))

        allExpired = True
        for i in self.regions:
            if i.regionExpired == False:
                log.log(3,"info",_("Region " + i.regionNodeName + " has not expired. Waiting"))
                allExpired = False

        self.__regionLock.acquire()
        if allExpired and not self.expiring:
            log.log(2,"info",_("All regions have expired. Marking layout as expired"))
            self.layoutExpired = True
            self.expiring = True

            # TODO: Check that there is something else to show before killing
            #       the layout off completely.


            # Enqueue region exit transitions by calling the dispose method on each regionManager
            for i in self.regions:
                i.dispose()
                
            self.__regionLock.release()
            return True
        else:
            self.__regionLock.release()
            if allExpired:
                return True
            
            return False

    def regionDisposed(self):
        log.log(2,"info",_("Region disposed. Checking if all regions have disposed"))

        allExpired = True
        for i in self.regions:
            if i.disposed == False:
                log.log(3,"info",_("Region " + i.regionNodeName + " has not disposed. Waiting"))
                allExpired = False

        self.__regionDisposeLock.acquire()
        if allExpired == True and not self.nextLayoutTriggered:
            log.log(2,"info",_("All regions have disposed. Marking layout as disposed"))
            self.layoutDisposed = True

            if self.hold:
                log.log(2,"info",_("Holding the splash screen until we're told otherwise"))
            else:
                log.log(2,"info",_("LayoutManager->parent->nextLayout()"))
                self.nextLayoutTriggered = True
                self.parent.nextLayout()
                
        self.__regionDisposeLock.release()

    def dispose(self):
        # Enqueue region exit transitions by calling the dispose method on each regionManager
        for i in self.regions:
            i.dispose()

        # TODO: Remove this? The exiting layout should be left for a transition object to transition with.
        #       Leaving in place for testing though.
        # self.p.enqueue("reset","")

class XiboRegionManager(Thread):
    def __init__(self,parent,player,layoutNodeName,layoutNodeNameExt,cn):
        log.log(3,"info",_("New XiboRegionManager instance created."))
        Thread.__init__(self)
        # Semaphore used to block this thread's execution once it has passed control off to the Media thread.
        # Lock is released by a callback from the libavg player (which returns control to this thread such that the
        # player thread never blocks.
        self.lock = Semaphore()
        self.tLock = Semaphore()

        # Variables
        self.p = player
        self.parent = parent
        self.regionNode = cn
        self.layoutNodeName = layoutNodeName
        self.layoutNodeNameExt = layoutNodeNameExt
        self.regionExpired = False
        self.regionNodeNameExt = "-" + str(self.p.nextUniqueId())
        self.regionNodeName = None
        self.width = None
        self.height = None
        self.top = None
        self.left = None
        self.zindex = None
        self.disposed = False
        self.disposing = False
        self.oneItemOnly = False
        self.previousMedia = None
        self.currentMedia = None

        # Calculate the region ID name
        try:
            self.regionNodeName = "R" + str(self.regionNode.attributes['id'].value) + self.regionNodeNameExt
        except KeyError:
            log.log(1,"error",_("Region XLF is invalid. Missing required id attribute"))
            self.regionExpired = True
            self.parent.regionElapsed()
            return


        # Calculate the region width
        try:
            self.width = int(self.regionNode.attributes['width'].value) * parent.l.scaleFactor
        except KeyError:
            log.log(1,"error",_("Region XLF is invalid. Missing required width attribute"))
            self.regionExpired = True
            self.parent.regionElapsed()
            return

        # Calculate the region height
        try:
            self.height =  int(self.regionNode.attributes['height'].value) * parent.l.scaleFactor
        except KeyError:
            log.log(1,"error",_("Region XLF is invalid. Missing required height attribute"))
            self.regionExpired = True
            self.parent.regionElapsed()
            return

        # Calculate the region top
        try:
            self.top = int(self.regionNode.attributes['top'].value) * parent.l.scaleFactor
        except KeyError:
            log.log(1,"error",_("Region XLF is invalid. Missing required top attribute"))
            self.regionExpired = True
            self.parent.regionElapsed()
            return

        # Calculate the region left
        try:
            self.left = int(self.regionNode.attributes['left'].value) * parent.l.scaleFactor
        except KeyError:
            log.log(1,"error",_("Region XLF is invalid. Missing required left attribute"))
            self.regionExpired = True
            self.parent.regionElapsed()
            return

        # Get region zindex
        try:
            self.zindex = int(self.regionNode.attributes['zindex'].value)
        except KeyError:
            self.zindex = 1

    def run(self):
        self.lock.acquire()
        self.tLock.acquire()
        log.log(3,"info",_("New XiboRegionManager instance running for region:") + self.regionNodeName)
        # Create a div for the region and add it
        tmpXML = '<div id="' + self.regionNodeName + '" width="' + str(self.width) + '" height="' + str(self.height) + '" x="' + str(self.left) + '" y="' + str(self.top) + '" opacity="1.0" />'
        self.p.enqueue('add',(tmpXML,self.layoutNodeName))

        #  * Iterate through the media items
        #  -> For each media, display on screen and set a timer to cause the next item to be shown
        #  -> attempt to acquire self.lock - which will block this thread. We will be woken by the callback
        #     to next() by the libavg player.
        #  * When all items complete, mark region complete by setting regionExpired = True and calling parent.regionElapsed()
        mediaCount = 0

        while self.disposed == False and self.oneItemOnly == False and self.disposing == False:
            for cn in self.regionNode.childNodes:
                if cn.nodeType == cn.ELEMENT_NODE and cn.localName == "media":
                    log.log(3,"info","Encountered media")
                    mediaCount = mediaCount + 1
                    if self.disposed == False and self.disposing == False:
                        type = str(cn.attributes['type'].value)
                        type = type[0:1].upper() + type[1:]
                        log.log(4,"info","Media is of type: " + type)
                        try:
                            import plugins.media
                            __import__("plugins.media." + type + "Media",None,None,[''])
                            self.currentMedia = eval("plugins.media." + type + "Media." + type + "Media")(log,self,self.p,cn)

                            # Transition between media here...
                            import plugins.transitions
                            try:
                                tmp1 = str(self.previousMedia.options['transOut'])
                                tmp1 = tmp1[0:1].upper() + tmp1[1:]
                            except:
                                tmp1 = ""

                            try:
                                tmp2 = str(self.currentMedia.options['transIn'])
                                tmp2 = tmp2[0:1].upper() + tmp2[1:]
                            except:
                                tmp2 = ""

                            trans = (tmp1,tmp2)

                            log.log(3,"info",_("Beginning transitions: " + str(trans)))
                            # The two transitions match. Let one plugin handle both.
                            if (trans[0] == trans[1]) and trans[0] != "":
                                self.currentMedia.add()
                                self.currentMedia.start()
                                try:
                                    __import__("plugins.transitions." + trans[0] + "Transition",None,None,[''])
                                    tmpTransition = eval("plugins.transitions." + trans[0] + "Transition." + trans[0] + "Transition")(log,self.p,self.previousMedia,self.currentMedia,self.tNext)
                                    tmpTransition.start()
                                except ImportError:
                                    __import__("plugins.transitions.DefaultTransition",None,None,[''])
                                    tmpTransition = plugins.transitions.DefaultTransition.DefaultTransition(log,self.p,self.previousMedia,self.currentMedia,self.tNext)
                                    tmpTransition.start()
                                self.tLock.acquire()
                            else:

                            # The two transitions don't match.
                            # Create two transition plugins and run them sequentially.
                                if (trans[0] != ""):
                                    try:
                                        __import__("plugins.transitions." + trans[0] + "Transition",None,None,[''])
                                        tmpTransition = eval("plugins.transitions." + trans[0] + "Transition." + trans[0] + "Transition")(log,self.p,self.previousMedia,None,self.tNext)
                                        tmpTransition.start()
                                    except ImportError:
                                        __import__("plugins.transitions.DefaultTransition",None,None,[''])
                                        tmpTransition = plugins.transitions.DefaultTransition.DefaultTransition(log,self.p,self.previousMedia,None,self.tNext)
                                        tmpTransition.start()
                                    self.tLock.acquire()

                                if (trans[1] != ""):
                                    self.currentMedia.add()
                                    self.currentMedia.start()
                                    try:
                                        __import__("plugins.transitions." + trans[1] + "Transition",None,None,[''])
                                        tmpTransition = eval("plugins.transitions." + trans[1] + "Transition." + trans[1] + "Transition")(log,self.p,None,self.currentMedia,self.tNext)
                                        tmpTransition.start()
                                    except ImportError:
                                        __import__("plugins.transitions.DefaultTransition",None,None,[''])
                                        tmpTransition = plugins.transitions.DefaultTransition.DefaultTransition(log,self.p,None,self.currentMedia,self.tNext)
                                        tmpTransition.start()
                                    self.tLock.acquire()
                                else:
                                    self.currentMedia.add()
                                    self.currentMedia.start()
                            # Cleanup
                            try:
                                # TODO: I removed an if self.disposing == False: here
                                # I _think_ this was just me being paranoid on getting rid of exceptions thrown by the player
                                # but it's more important that the media node knows it has disposed for stats generation.
                                
                                # Tell the media node to dispose itself.
                                self.previousMedia.dispose()
                                self.tLock.acquire()

                            except AttributeError:
                                pass

                            if self.disposing == False and self.disposed == False:
                                # Wait for the new media to finish
                                self.lock.acquire()
                            self.previousMedia = self.currentMedia
                            self.currentMedia = None
                        except ImportError as detail:
                            log.log(0,"error","Missing media plugin for media type " + type + ": " + str(detail))
                            # TODO: Do something with this layout? Blacklist?
                            self.lock.release()

            self.regionExpired = True
            if self.parent.regionElapsed():
                # If regionElapsed returns True, then the layout is on its way out so stop looping
                # Acheived by pretending to be a single item region
                self.oneItemOnly = True

            # If there's only one item, render it and leave it alone!
            if mediaCount == 1:
                self.oneItemOnly = True
                log.log(3,"info",_("Region has only one media: ") + self.regionNodeName)
        # End while loop

    def next(self):
        # Release the lock semaphore so that the run() method of the thread can continue.
        # Called by a callback from libavg
        # log.log(3,"info",_("XiboRegionManager") + " " + self.regionNodeName + ": " + _("Next Media Item"))

        # Do nothing if the layout has already been removed from the screen
        if self.disposed == True or self.disposing == True:
            return

        self.lock.release()

    def tNext(self):
        if self.disposed == True:
            return

        self.tLock.release()

    def dispose(self):
        self.disposing = True
        log.log(5,"info",self.regionNodeName + " is disposing.")
        rOptions = {}
        oNode = None

        # Perform any region exit transitions
        for cn in self.regionNode.childNodes:
            if cn.nodeType == cn.ELEMENT_NODE and cn.localName == "options":
                oNode = cn

        try:
            for cn in oNode.childNodes:
                if cn.localName != None:
                    rOptions[str(cn.localName)] = cn.childNodes[0].nodeValue
                    log.log(5,"info","Region Options: " + str(cn.localName) + " -> " + str(cn.childNodes[0].nodeValue))
        except AttributeError:
            rOptions["transOut"] = ""

        # Make the transition objects and pass in options
        # Once animation complete, they should call back to self.disposeTransitionComplete()
        transOut = str(rOptions["transOut"])
        if (transOut != ""):
            import plugins.transitions
            transOut = transOut[0:1].upper() + transOut[1:]
            log.log(5,"info",self.regionNodeName + " starting exit transition")
            try:
                __import__("plugins.transitions." + transOut + "Transition",None,None,[''])
                tmpTransition = eval("plugins.transitions." + transOut + "Transition." + transOut + "Transition")(log,self.p,self.previousMedia,None,self.disposeTransitionComplete,rOptions,None)
                tmpTransition.start()
                log.log(5,"info",self.regionNodeName + " control passed to Transition object.")
            except ImportError as detail:
                log.log(3,"error",self.regionNodeName + ": Unable to import requested Transition plugin. " + str(detail))
                self.disposeTransitionComplete()
        else:
            self.disposeTransitionComplete()

    def disposeTransitionComplete(self):
        # Notify the LayoutManager when these are complete.
        log.log(5,"info",self.regionNodeName + " is disposed.")
        self.disposed = True
        self.parent.regionDisposed()
        
        # Unlock the media loop and allow it to complete.
        self.lock.release()
        self.tLock.release()

#### Finish Layout/Region Managment

#### Scheduler Classes
class XiboLayout:
    def __init__(self,layoutID):
        self.layoutID = layoutID
        self.__setup()
        
    def __setup(self):
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

        # Tags assinged to this layout
        self.tags = []

        # Array of media names (to check against md5Cache later!)
        self.media = []

        # Checks
        self.schemaCheck = False
        self.mediaCheck = False
        self.scheduleCheck = True
        self.pluginCheck = True

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
                if self.backgroundImage == "":
                    self.backgroundImage = None
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
            return
            
        except xml.parsers.expat.ExpatError:
            # File doesn't exist. Keep the layout object for the
            # schedule information it may contain later.
            log.log(3,"info",_("File does not exist. Marking layout built without XLF file"))
            self.builtWithNoXLF = True
            return

        # Find all the media nodes
        mediaNodes = self.doc.getElementsByTagName('media')

        # Iterate over the media nodes and extract path names
        # Make a media object minus its Player (to prevent any accidents!) and ask it
        # what media it needs to run. This allows us to be extensible.
        for mn in mediaNodes:
            type = str(mn.attributes['type'].value)
            type = type[0:1].upper() + type[1:]
            try:
                import plugins.media
                __import__("plugins.media." + type + "Media",None,None,[''])
                tmpMedia = eval("plugins.media." + type + "Media." + type + "Media")(log,None,None,mn)
            except:
                self.pluginCheck = False
                log.log(0,"error",_("Plugin missing for media in layout ") + self.layoutID)
                return
            self.media = self.media + tmpMedia.requiredFiles()
        
        # Find all the tag nodes
        tagNodes = self.doc.getElementsByTagName('tag')
        
        # Iterate over the tag nodes and extract the tags
        for tag in tagNodes:
            self.tags.append(str(tag.firstChild.nodeValue))
        
        log.log(3,"info","Layout " + str(self.layoutID) + " has tags: " + str(self.tags)) 

    def canRun(self):
        # See if we were built with no XLF
        # If we were, attempt to set ourselves up
        # Otherwise return False
        if self.builtWithNoXLF:
            self.__setup()
            if self.builtWithNoXLF:
                return False
        
        self.mediaCheck = True

        # Loop through all the media items in the layout
        # Check them against md5Cache
        for tmpPath in self.media:
            if tmpPath in md5Cache:
                # Check if the md5 cache is old for this file
                try:
                    if not md5Cache[tmpPath].isValid():
                        self.mediaCheck = False
                        log.log(3,"warn",_("Layout ") + self.layoutID + _(" cannot run because MD5 is incorrect on ") + tmpPath)

                    if not os.path.isfile(tmpPath):
                        self.mediaCheck = False
                        log.log(0,"error",_("Layout ") + self.layoutID + _(" cannot run because file is missing: ") + tmpPath)
                except:
                    self.mediaCheck = False
                    log.log(0,"error",_("Layout ") + self.layoutID + _(" cannot run because an exception was thrown.") + tmpPath)
            else:
                self.mediaCheck = False
                log.log(3,"info",_("Layout ") + self.layoutID + _(" cannot run because file is missing from the md5Cache: ") + tmpPath)

        # See if the item is in a scheduled window to run

        log.log(3,"info",_("Layout ") + self.layoutID + " canRun(): schema-" + str(self.schemaCheck) + " media-" + str(self.mediaCheck) + " schedule-" + str(self.scheduleCheck) + " plugin-" + str(self.pluginCheck))
        return self.schemaCheck and self.mediaCheck and self.scheduleCheck and self.pluginCheck

    def resetSchedule(self):
        pass

    def addSchedule(self,fromDt,toDt):
        pass

    def children(self):
        return self.iter

class DummyScheduler(XiboScheduler):
    "Dummy scheduler - returns a list of layouts in rotation forever"
#    layoutList = ['1', '2', '3']
    layoutList = ['5','6']
    layoutIndex = 0

    def __init__(self,xmds,player):
        Thread.__init__(self)

    def run(self):
        pass

    def nextLayout(self):
        "Return the next valid layout"

        layout = XiboLayout(self.layoutList[self.layoutIndex])
        self.layoutIndex = self.layoutIndex + 1

        if self.layoutIndex == len(self.layoutList):
            self.layoutIndex = 0

        if layout.canRun() == False:
            log.log(3,"info",_("DummyScheduler: nextLayout() -> ") + str(layout.layoutID) + _(" is not ready to run."))
            if len(self.layoutList) > 1:
                return self.nextLayout()
            else:
                return XiboLayout("0")
        else:
            log.log(3,"info",_("DummyScheduler: nextLayout() -> ") + str(layout.layoutID))
            return layout

    def hasNext(self):
        "Return true if there are more layouts, otherwise false"
        log.log(3,"info",_("DummyScheduler: hasNext() -> true"))
        return True

class XmdsScheduler(XiboScheduler):
    "XMDS Scheduler. Retrieves the current schedule from XMDS."

    def __init__(self,xmds,player):
        Thread.__init__(self)
        self.xmds = xmds
        self.running = True
        self.__pointer = -1
        self.__layouts = []
        self.__lock = Semaphore()
        self.previousSchedule = "<schedule/>"
        self.p = player
        self.__collectLock = Semaphore()
        self.__collectLock.acquire()
        
        self.validTag = "default"

    def run(self):
        while self.running:
            self.interval = 300
            
            # Find out how long we should wait between updates.
            try:
                self.interval = int(config.get('Main','xmdsUpdateInterval'))
            except:
                # self.interval has been set to a sensible default in this case.
                log.log(0,"warning",_("No XMDS Update Interval specified in your configuration"))
                log.log(0,"warning",_("Please check your xmdsUpdateInterval configuration option"))
                log.log(0,"warning",_("A default value has been used:") + " " + str(self.interval) + " " + _("seconds"))
            
            # Call schedule on the webservice
            schedule = '<schedule/>'
            try:
                schedule = self.xmds.Schedule()
                log.log(5,"audit",_("XmdsScheduler: XMDS Schedule() returned ") + str(schedule))
                f = open(config.get('Main','libraryDir') + os.sep + 'schedule.xml','w')
                f.write(schedule)
                f.close()
            except IOError:
                log.log(0,"error",_("Error trying to cache Schedule to disk"))
            except XMDSException:
                log.log(0,"warning",_("XMDS RequiredFiles threw an exception"))
                try:
                    try:
                        f = open(config.get('Main','libraryDir') + os.sep + 'schedule.xml')
                        schedule = f.read()
                    finally:
                        f.close()
                except:
                    # Couldn't read or file doesn't exist. Either way, return the default blank schedule.
                    pass
            
            scheduleText = ""
            
            # TODO: Process the received schedule
            # If the schedule hasn't changed, do nothing.
            if self.previousSchedule != schedule:
                doc = minidom.parseString(schedule)
                tmpLayouts = doc.getElementsByTagName('layout')
            
                newLayouts = []
                for l in tmpLayouts:
                    layoutID = str(l.attributes['file'].value)
                    layoutFromDT = str(l.attributes['fromdt'].value)
                    layoutToDT = str(l.attributes['todt'].value)
                    flag = True
                    
                    # If the layout already exists, add this schedule to it
                    for g in newLayouts:
                        if g.layoutID == layoutID:
                            # Append Schedule
                            g.addSchedule(layoutFromDT,layoutToDT)
                            scheduleText += str(layoutID) + ', '
                            flag = False
                    
                    # The layout doesn't exist, add it and add a schedule for it
                    if flag:
                        tmpLayout = XiboLayout(layoutID)
                        tmpLayout.addSchedule(layoutFromDT,layoutToDT)
                        newLayouts.append(tmpLayout)
                        scheduleText += str(layoutID) + ', '
                        
                    # Swap the newLayouts array in to the live scheduler
                    self.__lock.acquire()
                    self.__layouts = newLayouts
                    self.__lock.release()
                    
                    log.updateSchedule(scheduleText)
            # End if previousSchedule != schedule
            
            log.log(3,"info",_("XmdsScheduler: Sleeping") + " " + str(self.interval) + " " + _("seconds"))
            self.p.enqueue('timer',(int(self.interval) * 1000,self.collect))
            self.__collectLock.acquire()
        # End while self.running
    
    def collect(self):
        self.__collectLock.release()

    def __len__(self):
        return len(self.__layouts)

    def nextLayout(self):
        "Return the next valid layout"
        
        # If there are no possible layouts then return the splash screen straight away.
        if len(self) == 0:
            return XiboLayout('0')
        
        # Consider each possible layout and see if it can run
        # Lock out the scheduler while we do this so that the
        # maths doesn't go horribly wrong!
        self.__lock.acquire()
        count = 0
        while count < len(self):
            self.__pointer = (self.__pointer + 1) % len(self)
            tmpLayout = self.__layouts[self.__pointer]
            
            if tmpLayout.canRun() and self.validTag in tmpLayout.tags:
                log.updateNowPlaying(str(tmpLayout.layoutID))
                self.__lock.release()
                return tmpLayout
            else:
                count = count + 1
        
        self.__lock.release()
        log.updateNowPlaying(str(tmpLayout.layoutID))
        return XiboLayout('0')

    def hasNext(self):
        "Return true if there are more layouts, otherwise false"
        log.log(3,"info",_("XmdsScheduler: hasNext() -> true"))
        return True
#### Finish Scheduler Classes

#### Switch Input Watcher ####
class SwitchWatcher(Thread):
    
    def __init__(self,scheduler,displayManager):
        Thread.__init__(self)
        self.scheduler = scheduler
        self.displayManager = displayManager
        self.tags = []
        
        try:
            self.defaultTag = config.get('LiftTags','default')
        except ConfigParser.NoOptionError:
            self.defaultTag = "default"
            log.log(0,"error",_("No LiftTags.default specified in your configuration. Defaulting to 'default'."))
        
        for i in range(0,7):
            try:
                self.tags.append(str(config.get('LiftTags','lift' + str(i))))
            except ConfigParser.NoOptionError:
                self.tags.append("lift" + str (i + 1))
                log.log(0,"error",_("No LiftTags.lift" + str(i) + " specified in your configuration. Defaulting to 'lift" + str(i + 1) + "'."))
        
        try:
            self.serialPort0 = config.get('Lift','serial0')
        except:
            self.serialPort0 = '/dev/ttyUSB0'
        
        try:
            self.serialPort1 = config.get('Lift','serial1')
        except:
            self.serialPort1 = '/dev/ttyUSB1'
        
    def run(self):
        
        state = [False,False,False,False,False,False,False,False]
        stats = ["","","","","","","",""]

        ser0 = None
        ser1 = None
        
        try:
            ser0 = serial.Serial(self.serialPort0)
        except serial.SerialException:
            log.log(0,"error","Unable to open configured serial port. Switch interface disabled: " + self.serialPort0)
            log.lights('Lift1','red')
            log.lights('Lift2','red')
            log.lights('Lift3','red')
            log.lights('Lift4','red')
            ser0 = False
        
        try:
            ser1 = serial.Serial(self.serialPort1)
        except serial.SerialException:
            log.log(0,"error","Unable to open configured serial port. Switch interface disabled: " + self.serialPort1)
            log.lights('Lift5','red')
            log.lights('Lift6','red')
            log.lights('Lift7','red')
            log.lights('Lift8','red')
            ser1 = False
            if ser0 == False:
                # No lifts are active. Quit now.
                return
        
        # Figure out which numbers to loop over
        if ser0 and ser1:
            # ie 0,4
            rS=0
            rF=5
            rD=4
        else:
            if ser0:
                # ie 0
                rS=0
                rF=1
                rD=4
            
            if ser1:
                # ie 4
                rS=4
                rF=5
                rD=4
        
        while True:
            flag = False
            offFlag = False
            
            for i in range(rS,rF,rD):
                if i == 0:
                    ser = ser0
                else:
                    ser = ser1
                    
                if ser.getCD() == state[i]:
                    if not state[i]:
                        self.scheduler.validTag = self.tags[i]
                        log.lights('Lift' + str(i + 1),'green')
                        flag = True
                        state[i] = True
                        stats[i] = str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
                    else:
                        log.lights('Lift' + str(i + 1),'grey')
                        state[i] = False
                        log.stat('event', stats[i], str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())), "lift" + str(i+1), "", "", "")
                        offFlag = True
                if ser.getDSR() == state[1 + i]:
                    if not state[1 + i]:
                        self.scheduler.validTag = self.tags[i + 1]
                        log.lights('Lift' + str(i + 2),'green')
                        flag = True
                        state[1 + i] = True
                        stats[1 + i] = str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
                    else:
                        log.lights('Lift' + str(i + 2),'grey')
                        state[1 + i] = False
                        log.stat('event', stats[1 + i], str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())), "lift" + str(i+2), "", "", "")
                        offFlag = True
                if ser.getCTS() == state[2 + i]:
                    if not state[2 + i]:
                        self.scheduler.validTag = self.tags[i + 2]
                        flag = True
                        log.lights('Lift' + str(i + 3),'green')
                        state[2 + i] = True
                        stats[2 + i] = str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
                    else:
                        log.lights('Lift' + str(i + 3),'grey')
                        state[2 + i] = False
                        log.stat('event', stats[2 + i], str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())), "lift" + str(i+3), "", "", "")
                        offFlag = True
                if ser.getRI() == state[3 + i]:
                    if not state[3 + i]:
                        self.scheduler.validTag = self.tags[i + 3]
                        flag = True
                        log.lights('Lift' + str(i + 4),'green')
                        state[3 + i] = True
                        stats[3 + i] = str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
                    else:
                        log.lights('Lift' + str(i + 4),'grey')
                        state[3 + i] = False
                        log.stat('event', stats[3 + i], str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())), "lift" + str(i+4), "", "", "")
                        offFlag = True
            
            if flag:
                log.updateLift(self.scheduler.validTag)
                self.displayManager.currentLM.dispose()
            
            if offFlag:
                # TODO: Could these be changed for or instead? I think they could.
                if (not state[0]) and (not state[1]) and (not state[2]) and (not state[3]) and (not state[4]) and (not state[5]) and (not state[6]) and (not state[7]):
                    self.scheduler.validTag = self.defaultTag
                    log.updateLift(self.scheduler.validTag)
                    self.displayManager.currentLM.dispose()
                            
            time.sleep(0.25)
            
    
#### End Switch Input Watcher ####

#### Webservice
class XMDSException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class XMDS:
    def __init__(self):
        # Semaphore to allow only one XMDS call to run check simultaneously
        self.checkLock = Semaphore()

        self.hasInitialised = False

        salt = None
        try:
            salt = config.get('Main','xmdsClientID')
        except:
            log.log(0,"error",_("No XMDS Client ID specified in your configuration"))
            log.log(0,"error",_("Please check your xmdsClientID configuration option"))
            exit(1)

        self.uuid = uuid.uuid5(uuid.NAMESPACE_DNS, salt)
        # Convert the UUID in to a SHA1 hash
        self.uuid = hashlib.sha1(str(self.uuid)).hexdigest()

        self.name = None
        try:
            self.name = config.get('Main','xmdsClientName')
        except:
            pass

        if self.name == None or self.name == "":
            import platform
            self.name = platform.node()

        self.key = None
        try:
            self.key = config.get('Main','xmdsKey')
        except:
            log.log(0,"error",_("No XMDS server key specified in your configuration"))
            log.log(0,"error",_("Please check your xmdsKey configuration option"))
            exit(1)

        # Setup a Proxy for XMDS
        self.xmdsUrl = None
        try:
            self.xmdsUrl = config.get('Main','xmdsUrl')
            if self.xmdsUrl[-1] != "/":
                self.xmdsUrl = self.xmdsUrl + "/"
            self.xmdsUrl = self.xmdsUrl + "xmds.php"
        except ConfigParser.NoOptionError:
            log.log(0,"error",_("No XMDS URL specified in your configuration"))
            log.log(0,"error",_("Please check your xmdsUrl configuration option"))
            exit(1)

        self.wsdlFile = self.xmdsUrl + '?wsdl'

    def getUUID(self):
        return str(self.uuid)

    def getName(self):
        return str(self.name)

    def getKey(self):
        return str(self.key)

    def check(self):
        if self.hasInitialised:
            return True
        else:
            self.checkLock.acquire()
            # Check again as we may have been called and blocked by another thread
            # doing this work for us.
            if self.hasInitialised:
                self.checkLock.release()
                return True
            
            self.server = None
            tries = 0
            while self.server == None and tries < 3:
                tries = tries + 1
                log.log(2,"info",_("Connecting to XMDS at ") + self.xmdsUrl + " " + _("Attempt") + " " + str(tries))
                try:
                    self.server = WSDL.Proxy(self.wsdlFile)
                    self.hasInitialised = True
                except xml.parsers.expat.ExpatError:
                    log.log(0,"error",_("Could not connect to XMDS."))
            # End While
            if self.server == None:
                self.checkLock.release()
                return False

        self.checkLock.release()
        return True

    def RequiredFiles(self):
        """Connect to XMDS and get a list of required files"""
        log.lights('RF','amber')
        req = None
        if self.check():
            try:
                # TODO: Change the final arguement to use the globally defined schema version once
                # there is a server that supports the schema to test against.
                req = self.server.RequiredFiles(self.getKey(),self.getUUID(),"1")
            except SOAPpy.Types.faultType, err:
                log.lights('RF','red')
                log.lights('RF','red')
                raise XMDSException("RequiredFiles: Incorrect arguments passed to XMDS.")
            except SOAPpy.Errors.HTTPError, err:
                log.lights('RF','red')
                log.log(0,"error",str(err))
                raise XMDSException("RequiredFiles: HTTP error connecting to XMDS.")
            except socket.error, err:
                log.lights('RF','red')
                log.log(0,"error",str(err))
                raise XMDSException("RequiredFiles: socket error connecting to XMDS.")
        else:
            log.log(0,"error","XMDS could not be initialised")
            log.lights('RF','grey')
            raise XMDSException("XMDS could not be initialised")

        log.lights('RF','green')
        return req
    
    def SubmitLog(self,logXml):
        response = None
        log.lights('Log','amber')
        
        if self.check():
            try:
                # response = self.server.SubmitLog(serverKey=self.getKey(),hardwareKey=self.getUUID(),logXml=logXml,version="1")
                response = self.server.SubmitLog("1",self.getKey(),self.getUUID(),logXml)
            except SOAPpy.Types.faultType, err:
                log.log(0,"error",str(err))
                log.lights('Log','red')
                raise XMDSException("SubmitLog: Incorrect arguments passed to XMDS.")
            except SOAPpy.Errors.HTTPError, err:
                log.log(0,"error",str(err))
                log.lights('Log','red')
                raise XMDSException("SubmitLog: HTTP error connecting to XMDS.")
            except socket.error, err:
                log.log(0,"error",str(err))
                log.lights('Log','red')
                raise XMDSException("SubmitLog: socket error connecting to XMDS.")
        else:
            log.log(0,"error","XMDS could not be initialised")
            log.lights('Log','grey')
            raise XMDSException("XMDS could not be initialised")
        
        log.lights('Log','green')
        return response
    
    def SubmitStats(self,statXml):
        response = None
        log.lights('Stat','amber')
        
        if self.check():
            try:
                response = self.server.SubmitStats(serverKey=self.getKey(),hardwareKey=self.getUUID(),statXml=statXml,version="1")
            except SOAPpy.Types.faultType, err:
                log.log(0,"error",str(err))
                log.lights('Stat','red')
                raise XMDSException("SubmitStats: Incorrect arguments passed to XMDS.")
            except SOAPpy.Errors.HTTPError, err:
                log.log(0,"error",str(err))
                log.lights('Stat','red')
                raise XMDSException("SubmitStats: HTTP error connecting to XMDS.")
            except socket.error, err:
                log.log(0,"error",str(err))
                log.lights('Stat','red')
                raise XMDSException("SubmitStats: socket error connecting to XMDS.")
        else:
            log.log(0,"error","XMDS could not be initialised")
            log.lights('Stat','grey')
            raise XMDSException("XMDS could not be initialised")
        
        log.lights('Stat','green')
        return response

    def Schedule(self):
        """Connect to XMDS and get the current schedule"""
        log.lights('S','amber')
        req = None
        if self.check():
            try:
                # TODO: Change the final arguement to use the globally defined schema version once
                # there is a server that supports the schema to test against.
                req = self.server.Schedule(self.getKey(),self.getUUID(),"1")
            except SOAPpy.Types.faultType, err:
                log.log(0,"error",str(err))
                log.lights('S','red')
                raise XMDSException("Schedule: Incorrect arguments passed to XMDS.")
            except SOAPpy.Errors.HTTPError, err:
                log.log(0,"error",str(err))
                log.lights('S','red')
                raise XMDSException("Schedule: HTTP error connecting to XMDS.")
            except socket.error, err:
                log.log(0,"error",str(err))
                log.lights('S','red')
                raise XMDSException("Schedule: socket error connecting to XMDS.")
        else:
            log.log(0,"error","XMDS could not be initialised")
            log.lights('S','grey')
            raise XMDSException("XMDS could not be initialised")

        log.lights('S','green')
        return req

    def GetFile(self,tmpPath,tmpType,tmpOffset,tmpChunk):
        """Connect to XMDS and download a file"""
        response = None
        log.lights('GF','amber')
        if self.check():
            try:
                # TODO: Change the final arguement to use the globally defined schema version once
                # there is a server that supports the schema to test against.
                response = self.server.GetFile(self.getKey(),self.getUUID(),tmpPath,tmpType,tmpOffset,tmpChunk,"1")
            except SOAPpy.Types.faultType, err:
                log.log(0,"error",str(err))
                log.lights('GF','red')
                raise XMDSException("GetFile: Incorrect arguments passed to XMDS.")
            except SOAPpy.Errors.HTTPError, err:
                log.log(0,"error",str(err))
                log.lights('GF','red')
                raise XMDSException("GetFile: HTTP error connecting to XMDS.")
            except socket.error, err:
                log.log(0,"error",str(err))
                log.lights('GF','red')
                raise XMDSException("GetFile: socket error connecting to XMDS.")
        else:
            log.log(0,"error","XMDS could not be initialised")
            log.lights('GF','grey')
            raise XMDSException("XMDS could not be initialised")

        log.lights('GF','green')
        return response

    def RegisterDisplay(self):
        """Connect to XMDS and attempt to register the client"""
        requireXMDS = False
        try:
            if config.get('Main','requireXMDS') == "true":
                requireXMDS = True
        except:
            pass

        if requireXMDS:
            log.lights('RD','amber')
            regReturn = ""
            regOK = "Display is active and ready to start."
            regInterval = 20
            tries = 0
            while regReturn != regOK:
                tries = tries + 1
                if self.check():
                    #TODO: Change the final arguement to use the globally defined schema version once
                    # there is a server that supports the schema to test against.
                    try:
                        regReturn = self.server.RegisterDisplay(self.getKey(),self.getUUID(),self.getName(),"1")
                        log.log(0,"info",regReturn)
                    except SOAPpy.Types.faultType, err:
                        log.lights('RD','red')
                        log.log(0,"error",str(err))
                    except SOAPpy.Errors.HTTPError, err:
                        log.lights('RD','red')
                        log.log(0,"error",str(err))
                    except socket.error, err:
                        log.lights('RD','red')
                        log.log(0,"error",str(err))

                if regReturn != regOK:
                    # We're not licensed. Sleep 20 * tries seconds and try again.
                    log.log(0,"info",_("Waiting for license to be issued, or connection restored to the webservice. Set requireXMDS=false to skip this check"))
                    log.lights('RD','red')
                    time.sleep(regInterval * tries)
            # End While
            log.lights('RD','green')
        else:
            if self.check():
                #TODO: Change the final arguement to use the globally defined schema version once
                # there  is a server that supports the schema to test against.
                try:
                    log.log(0,"info",self.server.RegisterDisplay(self.getKey(),self.getUUID(),self.getName(),"1"))
                    log.lights('RD','green')
                except SOAPpy.Types.faultType, err:
                    log.lights('RD','red')
                    log.log(0,"error",str(err))
                except SOAPpy.Errors.HTTPError, err:
                    log.lights('RD','red')
                    log.log(0,"error",str(err))
                except socket.error, err:
                    log.lights('RD','red')
                    log.log(0,"error",str(err))

#### Finish Websevrvice

class XiboDisplayManager:
    def __init__(self):
        pass

    def run(self):
        self.xmds = XMDS()
        
        logLevel = config.get('Logging','logLevel');
        print _("Log Level is: ") + logLevel;
        print _("Logging will be handled by: ") + config.get('Logging','logWriter')
        print _("Switching to new logger")

        global log
        logWriter = config.get('Logging','logWriter')
        log = eval(logWriter)(logLevel)
        log.setXmds(self.xmds)
        try:

            log.log(2,"info",_("Switched to new logger"))
        except:
            print logWriter + _(" does not implement the methods required to be a Xibo logWriter or does not exist.")
            print _("Please check your logWriter configuration.")
            exit(1)

        log.log(2,"info",_("New DisplayManager started"))

        # Create a XiboPlayer and start it running.
        self.Player = XiboPlayer(self)
        self.Player.start()

        # TODO: Display the splash screen
        self.currentLM = XiboLayoutManager(self, self.Player, XiboLayout('0'), 0, 1.0, True)
        self.currentLM.start()

        # Let the log object see the player so it can update the hidden info screen.
        log.setupInfo(self.Player)
        
        # Load a DownloadManager and start it running in its own thread
        try:
            downloaderName = config.get('Main','downloader')
            self.downloader = eval(downloaderName)(self.xmds,self.Player)
            self.downloader.start()
            log.log(2,"info",_("Loaded Download Manager ") + downloaderName)
        except ConfigParser.NoOptionError:
            log.log(0,"error",_("No DownloadManager specified in your configuration."))
            log.log(0,"error",_("Please check your Download Manager configuration."))
            exit(1)
        except:
            log.log(0,"error",downloaderName + _(" does not implement the methods required to be a Xibo DownloadManager or does not exist."))
            log.log(0,"error",_("Please check your Download Manager configuration.") + str(e))
            exit(1)
        # End of DownloadManager init

        # Load a scheduler and start it running in its own thread
        try:
            schedulerName = config.get('Main','scheduler')
            self.scheduler = eval(schedulerName)(self.xmds,self.Player)
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
        
        # Thread to watch the switch inputs and control the scheduler
        self.switch = SwitchWatcher(self.scheduler,self)
        self.switch.start()

        # Attempt to register with the webservice.
        # The RegisterDisplay code will block here if
        # we're configured not to play cached content on startup.
        self.xmds.RegisterDisplay()

        # Done with the splash screen. Let it advance...
        self.currentLM.hold = False
        self.currentLM.regionDisposed()

    def nextLayout(self):
        # TODO: Whole function is wrong. This is where layout transitions should be supported.
        # Needs careful consideration.

        # Deal with any existing LayoutManagers that might still be running
        try:
            if self.currentLM.isRunning == True:
                self.currentLM.dispose()
        except:
            pass

        # Store a reference to the current layout div so we can remove it
        tmpLayout = self.currentLM.layoutNodeName

        # New LayoutManager
        self.currentLM = XiboLayoutManager(self, self.Player, self.scheduler.nextLayout())
        log.log(2,"info",_("XiboLayoutManager: nextLayout() -> Starting new XiboLayoutManager with layout ") + str(self.currentLM.l.layoutID))
        self.currentLM.start()
        self.Player.enqueue('del',tmpLayout)

class XiboPlayer(Thread):
    "Class to handle libavg interactions"
    def __init__(self,parent):
        Thread.__init__(self)
        self.info = False
        self.q = Queue.Queue(0)
        self.uniqueId = 0
        self.dim = (int(config.get('Main','width')),int(config.get('Main','height')))
        self.currentFH = None
        self.parent = parent
        self.__lock = Semaphore()
        # Acquire the lock so that nothing can enqueue stuff until this thread starts
        self.__lock.acquire()

    def getDimensions(self):
        return self.dim

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
        self.player.volume = 1
        
        # Calculate the information window
        infoX = (int(config.get('Main','width')) - 400) / 2
        infoY = (int(config.get('Main','height')) - 300) / 2
        
        # If the info window is bigger than the client, stick it in the top left corner.
        if infoX < 0:
            infoX = 0
        if infoY < 0:
            infoY = 0
        
        # Build the XML that defines the avg node and divs for screen and information
        avgContent = '<avg id="main" width="'
        avgContent += config.get('Main','width')
        avgContent += '" height="'
        avgContent += config.get('Main','height')
        avgContent += '"><div id="screen"/>'
        avgContent += '<div id="info" width="400" height="300" x="'
        avgContent += str(infoX)
        avgContent += '" y="'
        avgContent += str(infoY)
        avgContent += '" opacity="0" />'
        avgContent += '</avg>'
        self.player.loadString(avgContent)
        avgNode = self.player.getElementByID("main")
        avgNode.setEventHandler(avg.KEYDOWN,avg.NONE,self.keyDown)
        self.currentFH = self.player.setOnFrameHandler(self.frameHandle)
        
        # Release the lock so other threads can add content
        self.__lock.release()
        self.player.play()
    
    def keyDown(self,e):
        if e.keystring == "i":
            if self.info:
                self.info = False
                self.enqueue('setOpacity',('info',0))
            else:
                self.info = True
                self.enqueue('setOpacity',('info',1))
                
        if self.info:
            # Process key strokes that are only active when the info
            # screen is showing
            if e.keystring == "n":
                self.parent.currentLM.dispose()
            
            if e.keystring == "r":
                self.parent.downloader.collect()
                self.parent.scheduler.collect()
            
            if e.keystring == "q":
                #TODO: Fully implement a proper quit function
                # Allow threads a chance to stop nicely before finally killing
                # the lot off.
                self.parent.downloader.running = False
                self.parent.downloader.collect()
                self.parent.downloader.join()
                self.parent.scheduler.running = False
                self.parent.scheduler.collect()
                self.parent.scheduler.join()
                self.player.stop()
                os._exit(0)

    def enqueue(self,command,data):
        log.log(3,"info","Enqueue: " + str(command) + " " + str(data))
        self.__lock.acquire()
        self.q.put((command,data))
        if self.currentFH == None:
            self.currentFH = self.player.setOnFrameHandler(self.frameHandle)
        self.__lock.release()
        log.log(3,"info",_("Queue length is now") + " " + str(self.q.qsize()))

    def frameHandle(self):
        "Called on each new libavg frame. Takes queued commands and executes them"
        self.__lock.acquire()
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
                if data[0] == "linear":
                    animation = anim.LinearAnim(currentNode,data[3],data[2],data[4],data[5],False,data[6])
            elif cmd == "play":
                currentNode = self.player.getElementByID(data)
                currentNode.play()
            elif cmd == "pause":
                currentNode = self.player.getElementByID(data)
                currentNode.pause()
            elif cmd == "stop":
                currentNode = self.player.getElementByID(data)
                currentNode.stop()
            elif cmd == "resize":
                currentNode = self.player.getElementByID(data[0])
                dimension = currentNode.getMediaSize()
                # log.log(1,'info',"Media dimensions: " + str(dimension))
                scaleFactor = min((float(data[1]) / dimension[0]),(float(data[2]) / dimension[1]))
                # log.log(1,'info',"Scale Factor: " + str(scaleFactor))
                currentNode.width = dimension[0] * scaleFactor
                currentNode.height = dimension[1] * scaleFactor
                if data[3] == 'left':
                    currentNode.x = 0
                elif data[3] == 'centre':
                    currentNode.x = (float(data[1]) - currentNode.width) / 2
                elif data[3] == 'right':
                    currentNode.x = (float(data[1]) - currentNode.width)
                if data[4] == 'top':
                    currentNode.y = 0
                elif data[4] == 'centre':
                    currentNode.y = (float(data[2]) - currentNode.height) / 2
                elif data[4] == 'bottom':
                    currentNode.y = (float(data[2]) - currentNode.height)
            elif cmd == "timer":
                self.player.setTimeout(data[0],data[1])
            elif cmd == "eofCallback":
                currentNode = self.player.getElementByID(data[0])
                currentNode.setEOFCallback(data[1])
            elif cmd == "setOpacity":
                currentNode = self.player.getElementByID(data[0])
                currentNode.opacity = data[1]
            self.q.task_done()
            # Call ourselves again to action any remaining queued items
            # This does not make an infinite loop since when all queued items are processed
            # A Queue.Empty exception is thrown and this whole block is skipped.
            self.__lock.release()
            self.frameHandle()
        except Queue.Empty:
            self.player.clearInterval(self.currentFH)
            self.currentFH = None
            self.__lock.release()
        except RuntimeError as detail:
            log.log(1,"error",_("A runtime error occured: ") + str(detail))
            self.__lock.release()
        # TODO: Put this catchall back when finished debugging.
        except:
               # log.log(0,"error",_("An unspecified error occured: ") + str(sys.exc_info()[0]))
               self.__lock.release()
               log.log(0,"audit",str(cmd) + " : " + str(data))

class XiboClient:
    "Main Xibo DisplayClient Class. May (in time!) host many DisplayManager classes"

    def __init__(self):
        pass

    def play(self):
        global version
        print _("Xibo Client v") + version

        global schemaVersion
        global log

        print _("Reading default configuration")
        global config
        config = ConfigParser.ConfigParser()
        config.readfp(open('defaults.cfg'))

        print _("Reading user configuration")
        config.read(['site.cfg', os.path.expanduser('~/.xibo')])

        # Store a dictionary of XiboFile objects so we know how recently
        # we last checked a file was present and correct.
        global md5Cache
        md5Cache = defaultdict(XiboFile)

        self.dm = XiboDisplayManager()

        self.dm.run()

# Main - create a XiboClient and run
gettext.install("messages", "locale")

xc = XiboClient()
xc.play()

