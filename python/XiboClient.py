#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# Xibo - Digitial Signage - http://www.xibo.org.uk
# Copyright (C) 2009-2011 Alex Harrington
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
import fnmatch
import re
import datetime
import sys
import socket
import inspect
from collections import defaultdict
from threading import Thread, Semaphore
import threading
import urlparse
import PIL.Image
import math

version = "1.3.1"

# What layout schema version is supported
schemaVersion = 1

#### Abstract Classes
class XiboLog:
    "Abstract Class - Interface for Loggers"
    level = 0
    def __init__(self, level): abstract
    def log(self, level, category, message, osd = False): abstract
    def stat(self, statType, fromDT, toDT, tag, layoutID, scheduleID, mediaID): abstract
    def setXmds(self, xmds):
        pass
    def flush(self):
        pass
    def setupInfo(self, p):
        self.p = p
        
        try:
            self.liftEnabled = config.get('Lift', 'enabled')
            if self.liftEnabled == "false":
                self.liftEnabled = False
                log.log(3, "audit", _("Disabling lift functionality in Logger"))
            else:
                self.liftEnabled = True
                log.log(3, "audit", _("Enabling lift functionality in Logger"))
        except:
            self.liftEnabled = False
            log.log(3, "error", _("Lift->enabled not defined in configuration. Disabling lift functionality in Logger"))
        
        # Populate the info screen
        # Background.
        tmpXML = '<rect fillcolor="ffffff" id="infoBG" fillopacity="0.75" size="(400,300)" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        
        # Logo + version bottom right
        tmpXML = '<image href="resources/logo.png" id="infoLOGO" opacity="1" width="50" height="18" x="345" y="276" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        tmpXML = '<words x="290" y="280" opacity="1" text="v' + version + '" font="Arial" color="000000" fontsize="12" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        
        # Required Files Traffic Light
        tmpXML = '<image href="resources/dotgrey.png" id="infoRFGrey" opacity="1" width="20" height="20" x="5" y="275" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        tmpXML = '<image href="resources/dotred.png" id="infoRFRed" opacity="0" width="20" height="20" x="5" y="275" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        tmpXML = '<image href="resources/dotamber.png" id="infoRFAmber" opacity="0" width="20" height="20" x="5" y="275" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        tmpXML = '<image href="resources/dotgreen.png" id="infoRFGreen" opacity="0" width="20" height="20" x="5" y="275" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        tmpXML = '<words x="10" y="270" opacity="1" text="Required Files" font="Arial" color="000000" fontsize="10" angle="-1.57079633" pivot="(0,0)"/>'
        self.p.enqueue('add' ,(tmpXML, 'info'))
        
        # GetFile Traffic Light
        tmpXML = '<image href="resources/dotgrey.png" id="infoGFGrey" opacity="1" width="20" height="20" x="30" y="275" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        tmpXML = '<image href="resources/dotred.png" id="infoGFRed" opacity="0" width="20" height="20" x="30" y="275" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        tmpXML = '<image href="resources/dotamber.png" id="infoGFAmber" opacity="0" width="20" height="20" x="30" y="275" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        tmpXML = '<image href="resources/dotgreen.png" id="infoGFGreen" opacity="0" width="20" height="20" x="30" y="275" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        tmpXML = '<words x="35" y="270" opacity="1" text="Get File" font="Arial" color="000000" fontsize="10" angle="-1.57079633" pivot="(0,0)"/>'
        self.p.enqueue('add', (tmpXML, 'info'))
        tmpXML = '<words id="infoRunningDownloads" x="37" y="278" opacity="1" text="0" font="Arial" color="000000" fontsize="10" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        
        # Schedule Traffic Light
        tmpXML = '<image href="resources/dotgrey.png" id="infoSGrey" opacity="1" width="20" height="20" x="55" y="275" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        tmpXML = '<image href="resources/dotred.png" id="infoSRed" opacity="0" width="20" height="20" x="55" y="275" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        tmpXML = '<image href="resources/dotamber.png" id="infoSAmber" opacity="0" width="20" height="20" x="55" y="275" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        tmpXML = '<image href="resources/dotgreen.png" id="infoSGreen" opacity="0" width="20" height="20" x="55" y="275" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        tmpXML = '<words x="60" y="270" opacity="1" text="Schedule" font="Arial" color="000000" fontsize="10" angle="-1.57079633" pivot="(0,0)"/>'
        self.p.enqueue('add', (tmpXML, 'info'))
        
        # RegisterDisplay Traffic Light
        tmpXML = '<image href="resources/dotgrey.png" id="infoRDGrey" opacity="1" width="20" height="20" x="80" y="275" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        tmpXML = '<image href="resources/dotred.png" id="infoRDRed" opacity="0" width="20" height="20" x="80" y="275" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        tmpXML = '<image href="resources/dotamber.png" id="infoRDAmber" opacity="0" width="20" height="20" x="80" y="275" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        tmpXML = '<image href="resources/dotgreen.png" id="infoRDGreen" opacity="0" width="20" height="20" x="80" y="275" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        tmpXML = '<words x="85" y="270" opacity="1" text="Register Display" font="Arial" color="000000" fontsize="10" angle="-1.57079633" pivot="(0,0)"/>'
        self.p.enqueue('add', (tmpXML, 'info'))
        
        # Logs Traffic Light
        tmpXML = '<image href="resources/dotgrey.png" id="infoLogGrey" opacity="1" width="20" height="20" x="105" y="275" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        tmpXML = '<image href="resources/dotred.png" id="infoLogRed" opacity="0" width="20" height="20" x="105" y="275" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        tmpXML = '<image href="resources/dotamber.png" id="infoLogAmber" opacity="0" width="20" height="20" x="105" y="275" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        tmpXML = '<image href="resources/dotgreen.png" id="infoLogGreen" opacity="0" width="20" height="20" x="105" y="275" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        tmpXML = '<words x="110" y="270" opacity="1" text="Log" font="Arial" color="000000" fontsize="10" angle="-1.57079633" pivot="(0,0)"/>'
        self.p.enqueue('add', (tmpXML, 'info'))
        
        # Stats Traffic Light
        tmpXML = '<image href="resources/dotgrey.png" id="infoStatGrey" opacity="1" width="20" height="20" x="130" y="275" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        tmpXML = '<image href="resources/dotred.png" id="infoStatRed" opacity="0" width="20" height="20" x="130" y="275" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        tmpXML = '<image href="resources/dotamber.png" id="infoStatAmber" opacity="0" width="20" height="20" x="130" y="275" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        tmpXML = '<image href="resources/dotgreen.png" id="infoStatGreen" opacity="0" width="20" height="20" x="130" y="275" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        tmpXML = '<words x="135" y="270" opacity="1" text="Stats" font="Arial" color="000000" fontsize="10" angle="-1.57079633" pivot="(0,0)"/>'
        self.p.enqueue('add', (tmpXML, 'info'))

        # Offline Update traffic light
        tmpXML = '<image href="resources/dotamber.png" id="offlineUpdateAmber" opacity="0" width="20" height="20" x="20" y="20" />'
        self.p.enqueue('add', (tmpXML, 'offlineUpdate'))
        tmpXML = '<image href="resources/dotgreen.png" id="offlineUpdateGreen" opacity="0" width="20" height="20" x="20" y="20" />'
        self.p.enqueue('add', (tmpXML, 'offlineUpdate'))
        
        # IP Address
        tmpXML = '<words x="5" y="5" opacity="1" text="IP Address: " font="Arial" color="000000" fontsize="11" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        tmpXML = '<words id="infoIP" x="75" y="5" opacity="1" text="" font="Arial" color="000000" fontsize="11" width="180" linespacing="10" alignment="left" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        
        # Disk Space
        tmpXML = '<words x="5" y="18" opacity="1" text="Disk Space: " font="Arial" color="000000" fontsize="11" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        tmpXML = '<words id="infoDisk" x="75" y="18" opacity="1" text="" font="Arial" color="000000" fontsize="11" width="180" linespacing="10" alignment="left" />'
        self.p.enqueue('add', (tmpXML, 'info'))

        # Lift Traffic Lights
        if self.liftEnabled:
            tmpXML = '<image href="resources/dotgrey.png" id="infoLift1Grey" opacity="1" width="5" height="5" x="165" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotred.png" id="infoLift1Red" opacity="0" width="5" height="5" x="165" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotamber.png" id="infoLift1Amber" opacity="0" width="5" height="5" x="165" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotgreen.png" id="infoLift1Green" opacity="0" width="5" height="5" x="165" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            
            tmpXML = '<image href="resources/dotgrey.png" id="infoLift2Grey" opacity="1" width="5" height="5" x="170" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotred.png" id="infoLift2Red" opacity="0" width="5" height="5" x="170" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotamber.png" id="infoLift2Amber" opacity="0" width="5" height="5" x="170" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotgreen.png" id="infoLift2Green" opacity="0" width="5" height="5" x="170" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            
            tmpXML = '<image href="resources/dotgrey.png" id="infoLift3Grey" opacity="1" width="5" height="5" x="175" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotred.png" id="infoLift3Red" opacity="0" width="5" height="5" x="175" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotamber.png" id="infoLift3Amber" opacity="0" width="5" height="5" x="175" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotgreen.png" id="infoLift3Green" opacity="0" width="5" height="5" x="175" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))

            tmpXML = '<image href="resources/dotgrey.png" id="infoLift4Grey" opacity="1" width="5" height="5" x="180" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotred.png" id="infoLift4Red" opacity="0" width="5" height="5" x="180" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotamber.png" id="infoLift4Amber" opacity="0" width="5" height="5" x="180" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotgreen.png" id="infoLift4Green" opacity="0" width="5" height="5" x="180" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            
            tmpXML = '<image href="resources/dotgrey.png" id="infoLift5Grey" opacity="1" width="5" height="5" x="190" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotred.png" id="infoLift5Red" opacity="0" width="5" height="5" x="190" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotamber.png" id="infoLift5Amber" opacity="0" width="5" height="5" x="190" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotgreen.png" id="infoLift5Green" opacity="0" width="5" height="5" x="190" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            
            tmpXML = '<image href="resources/dotgrey.png" id="infoLift6Grey" opacity="1" width="5" height="5" x="195" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotred.png" id="infoLift6Red" opacity="0" width="5" height="5" x="195" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotamber.png" id="infoLift6Amber" opacity="0" width="5" height="5" x="195" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotgreen.png" id="infoLift6Green" opacity="0" width="5" height="5" x="195" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            
            tmpXML = '<image href="resources/dotgrey.png" id="infoLift7Grey" opacity="1" width="5" height="5" x="200" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotred.png" id="infoLift7Red" opacity="0" width="5" height="5" x="200" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotamber.png" id="infoLift7Amber" opacity="0" width="5" height="5" x="200" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotgreen.png" id="infoLift7Green" opacity="0" width="5" height="5" x="200" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            
            tmpXML = '<image href="resources/dotgrey.png" id="infoLift8Grey" opacity="1" width="5" height="5" x="205" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotred.png" id="infoLift8Red" opacity="0" width="5" height="5" x="205" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotamber.png" id="infoLift8Amber" opacity="0" width="5" height="5" x="205" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotgreen.png" id="infoLift8Green" opacity="0" width="5" height="5" x="205" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))

            tmpXML = '<image href="resources/dotgrey.png" id="infoLift9Grey" opacity="1" width="5" height="5" x="215" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotred.png" id="infoLift9Red" opacity="0" width="5" height="5" x="215" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotamber.png" id="infoLift9Amber" opacity="0" width="5" height="5" x="215" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotgreen.png" id="infoLift9Green" opacity="0" width="5" height="5" x="215" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            
            tmpXML = '<image href="resources/dotgrey.png" id="infoLift10Grey" opacity="1" width="5" height="5" x="220" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotred.png" id="infoLift10Red" opacity="0" width="5" height="5" x="220" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotamber.png" id="infoLift10Amber" opacity="0" width="5" height="5" x="220" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotgreen.png" id="infoLift10Green" opacity="0" width="5" height="5" x="220" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            
            tmpXML = '<image href="resources/dotgrey.png" id="infoLift11Grey" opacity="1" width="5" height="5" x="225" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotred.png" id="infoLift11Red" opacity="0" width="5" height="5" x="225" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotamber.png" id="infoLift11Amber" opacity="0" width="5" height="5" x="225" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotgreen.png" id="infoLift11Green" opacity="0" width="5" height="5" x="225" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))

            tmpXML = '<image href="resources/dotgrey.png" id="infoLift12Grey" opacity="1" width="5" height="5" x="230" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotred.png" id="infoLift12Red" opacity="0" width="5" height="5" x="230" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotamber.png" id="infoLift12Amber" opacity="0" width="5" height="5" x="230" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotgreen.png" id="infoLift12Green" opacity="0" width="5" height="5" x="230" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            
            tmpXML = '<image href="resources/dotgrey.png" id="infoLift13Grey" opacity="1" width="5" height="5" x="240" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotred.png" id="infoLift13Red" opacity="0" width="5" height="5" x="240" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotamber.png" id="infoLift13Amber" opacity="0" width="5" height="5" x="240" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotgreen.png" id="infoLift13Green" opacity="0" width="5" height="5" x="240" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            
            tmpXML = '<image href="resources/dotgrey.png" id="infoLift14Grey" opacity="1" width="5" height="5" x="245" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotred.png" id="infoLift14Red" opacity="0" width="5" height="5" x="245" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotamber.png" id="infoLift14Amber" opacity="0" width="5" height="5" x="245" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotgreen.png" id="infoLift14Green" opacity="0" width="5" height="5" x="245" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            
            tmpXML = '<image href="resources/dotgrey.png" id="infoLift15Grey" opacity="1" width="5" height="5" x="250" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotred.png" id="infoLift15Red" opacity="0" width="5" height="5" x="250" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotamber.png" id="infoLift15Amber" opacity="0" width="5" height="5" x="250" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotgreen.png" id="infoLift15Green" opacity="0" width="5" height="5" x="250" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            
            tmpXML = '<image href="resources/dotgrey.png" id="infoLift16Grey" opacity="1" width="5" height="5" x="255" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotred.png" id="infoLift16Red" opacity="0" width="5" height="5" x="255" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotamber.png" id="infoLift16Amber" opacity="0" width="5" height="5" x="255" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))
            tmpXML = '<image href="resources/dotgreen.png" id="infoLift16Green" opacity="0" width="5" height="5" x="255" y="285" />'
            self.p.enqueue('add', (tmpXML, 'info'))

            # Lift Tag
            tmpXML = '<words id="infoLiftTag" x="165" y="265" opacity="1" text="Current Tag: default" font="Arial" color="000000" fontsize="11" />'
            self.p.enqueue('add', (tmpXML, 'info'))
        
        # Schedule
        tmpXML = '<words x="5" y="75" opacity="1" text="Schedule" font="Arial" color="000000" fontsize="14" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        tmpXML = '<words id="infoCurrentSchedule" x="5" y="90" opacity="1" text="" font="Arial" color="000000" fontsize="11" width="180" linespacing="10" alignment="left" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        
        # Now Playing
        tmpXML = '<words x="5" y="40" opacity="1" text="Now Playing" font="Arial" color="000000" fontsize="14" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        tmpXML = '<words id="infoNowPlaying" x="5" y="55" opacity="1" text="" font="Arial" color="000000" fontsize="11" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        
        # Media
        tmpXML = '<words x="205" y="5" opacity="1" text="Media" font="Arial" color="000000" fontsize="14" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        tmpXML = '<words id="infoMedia" x="205" y="20" opacity="1" text="" font="Arial" color="000000" fontsize="11" />'
        self.p.enqueue('add', (tmpXML, 'info'))

        # On Screen Logging
        tmpXML = '<rect fillcolor="ffffff" id="osLogBG" fillopacity="0.75" size="(%d,%d)" />' % (self.p.osLogX, 20)
        self.p.enqueue('add', (tmpXML, 'osLog'))
        tmpXML = '<words id="osLogText" x="5" y="3" opacity="1" text="Xibo Client v%s" font="Arial" color="000000" fontsize="11" />' % version
        self.p.enqueue('add', (tmpXML, 'osLog'))
    
    def lights(self, field, value):
        if value == "green":
            self.p.enqueue('setOpacity', ("info" + field + "Green", 1))
            self.p.enqueue('setOpacity', ("info" + field + "Grey", 0))
            self.p.enqueue('setOpacity', ("info" + field + "Amber", 0))
            self.p.enqueue('setOpacity', ("info" + field + "Red", 0))
        if value == "red":
            self.p.enqueue('setOpacity', ("info" + field + "Green", 0))
            self.p.enqueue('setOpacity', ("info" + field + "Grey", 0))
            self.p.enqueue('setOpacity', ("info" + field + "Amber", 0))
            self.p.enqueue('setOpacity', ("info" + field + "Red", 1))
        if value == "amber":
            self.p.enqueue('setOpacity', ("info" + field + "Green", 0))
            self.p.enqueue('setOpacity', ("info" + field + "Grey", 0))
            self.p.enqueue('setOpacity', ("info" + field + "Amber", 1))
            self.p.enqueue('setOpacity', ("info" + field + "Red", 0))
        if value == "grey":
            self.p.enqueue('setOpacity', ("info" + field + "Green", 0))
            self.p.enqueue('setOpacity', ("info" + field + "Grey", 1))
            self.p.enqueue('setOpacity', ("info" + field + "Amber", 0))
            self.p.enqueue('setOpacity', ("info" + field + "Red", 0))
        if value == "start":
            self.p.enqueue('setOpacity', ("%sAmber" % field, 1))
            self.p.enqueue('setOpacity', ("%sGreen" % field, 0))
        if value == "finish":
            self.p.enqueue('setOpacity', ("%sAmber" % field, 0))
            self.p.enqueue('setOpacity', ("%sGreen" % field, 1))
            self.p.enqueue('anim', ('fadeOut', '%sGreen' % field, 3000, None))

    def updateSchedule(self, schedule):
        self.p.enqueue('del', 'infoCurrentSchedule')
        tmpXML = '<words id="infoCurrentSchedule" x="5" y="90" opacity="1" text="' + schedule + '" font="Arial" color="000000" fontsize="11" width="180" linespacing="10" alignment="left" />'
        self.p.enqueue('add', (tmpXML, 'info'))

    def updateNowPlaying(self, now):
        self.p.enqueue('del', 'infoNowPlaying')
        tmpXML = '<words id="infoNowPlaying" x="5" y="55" opacity="1" text="' + now + '" font="Arial" color="000000" fontsize="11" />'
        self.p.enqueue('add', (tmpXML, 'info'))

    def updateMedia(self, media):
        self.p.enqueue('del', 'infoMedia')
        tmpXML = '<words id="infoMedia" x="205" y="20" opacity="1" font="Arial" color="000000" fontsize="11" width="180">' + media + '</words>'
        self.p.enqueue('add', (tmpXML, 'info'))
    
    def updateRunningDownloads(self, num):
        self.p.enqueue('del', 'infoRunningDownloads')
        tmpXML = '<words id="infoRunningDownloads" x="37" y="278" opacity="1" text="' + str(num) + '" font="Arial" color="000000" fontsize="10" />'
        self.p.enqueue('add', (tmpXML, 'info'))
    
    def updateIP(self, serverIP):
        self.p.enqueue('del', 'infoIP')
        tmpXML = '<words id="infoIP" x="75" y="5" opacity="1" text="' + str(serverIP) + '" font="Arial" color="000000" fontsize="10" />'
        self.p.enqueue('add', (tmpXML, 'info'))

    def updateFreeSpace(self, tup):
        perc = int((tup[1] * 1.0 / tup[0]) * 100)
        self.p.enqueue('del', 'infoDisk')
        tmpXML = '<words id="infoDisk" x="75" y="18" opacity="1" text="' + self.bytestr(tup[1]) + ' (' + str(perc) + '%) free" font="Arial" color="000000" fontsize="10" />'
        self.p.enqueue('add', (tmpXML, 'info'))
        
    # Convert a value in bytes to human readable format
    # Taken from http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
    # By Sridhar Ratnakumar
    # Assumed Public Domain
    def bytestr(self, size):
        for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return "%3.1f %s" % (size, x)
            size /= 1024.0
            
    def updateLift(self, tag):
        # Break out if lift is disabled
        if not self.liftEnabled:
            return
        
        self.p.enqueue('del', 'infoLiftTag')
        tmpXML = '<words id="infoLiftTag" x="165" y="265" opacity="1" text="Current Tag: ' + tag + '" font="Arial" color="000000" fontsize="11" />'
        self.p.enqueue('add', (tmpXML, 'info'))

    def osLog(self, message):
        self.p.enqueue('del', 'osLogText')
        tmpXML = '<words id="osLogText" x="5" y="3" opacity="1" text="%s" font="Arial" color="000000" fontsize="11" />' % message
        self.p.enqueue('add', (tmpXML, 'osLog'))

class XiboScheduler(Thread):
    "Abstract Class - Interface for Schedulers"
    def run(self): abstract
    def nextLayout(self): abstract
    def hasNext(self): abstract
#### Finish Abstract Classes

#### Log Classes
class XiboLogSplit(XiboLog):
    "Xibo Log Splitter - so log output can go to two log objects"
    # Currently non-functional
    def __init__(self,level):
        self.level = int(level)
        
        logWriter1 = config.get('Logging','splitLogWriter1')
        logWriter2 = config.get('Logging','splitLogWriter2')
        
        self.log1 = eval(logWriter1)(self.level)
        self.log2 = eval(logWriter2)(self.level)
        
        self.log(2,"info",_("XiboLogSplit logger started at level ") + str(level))
        
    def log(self, severity, category, message, osd=False):
        self.log1.log(severity, category, message, osd)
        self.log2.log(severity, category, message, osd)
        
    def stat(self, statType, fromDT, toDT, tag, layoutID, scheduleID, mediaID=""):
        self.log1.stat(statType, fromDT, toDT, tag, layoutID, scheduleID, mediaID)
        self.log2.stat(statType, fromDT, toDT, tag, layoutID, scheduleID, mediaID)
        
    def flush(self):
        self.log1.flush()
        self.log2.flush()

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

    def log(self, severity, category, message, osd=False):
        if self.level >= severity:
            
            # Define these two here incase an exception is thrown below.
            callingMethod = "unknown"
            callingClass = ""
            
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

        # If osLog is enabled, update the status
        if osd and self.p.osLog:
            self.osLog(message)

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

    def log(self, severity, category, message, osd=False):
        if self.level >= severity:
            print "LOG: " + str(time.time()) + " " + str(severity) + " " + category + " " + message

        # If osLog is enabled, update the status
        if osd and self.p.osLog:
            self.osLog(message)

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
            statsOn = config.get('Stats','collect')
            if statsOn == 'true':
                self.statsOn = True
            else:
                self.statsOn = False
        except ConfigParser.NoOptionError:
            self.statsOn = False        
        
        try:
            self.statsQueueSize = int(config.get('Stats','queueSize'))
        except ConfigParser.NoOptionError:
            self.statsQueueSize = 99
            
        self.worker = XiboLogXmdsWorker(self.logs,self.stats,self.statsQueueSize)
        self.worker.start()
    
    # Fast non-blocking log and stat functions
    # Logs and Stats pushed in native format on to the queue.
    # A worker thread will then format the messages in to XML
    # ready for transmission to the server.
    
    def log(self, severity, category, message, osd=False):
        
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

        # If osLog is enabled, update the status
        if osd and self.p.osLog:
            self.osLog(message)

    def stat(self, statType, fromDT, toDT, tag, layoutID, scheduleID, mediaID):
        if self.statsOn:
            self.stats.put((statType,fromDT,toDT,tag,layoutID,scheduleID,mediaID),False)
        return
        
    def setXmds(self,xmds):
        self.worker.xmds = xmds
    
    def flush(self):
        # TODO: Seems to cause the client to hang on quit?
        if not self.worker.xmds == None:
            self.worker.flush = True
            self.worker.process()

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
        
        self.flush = False
        self.processing = False
        self.__lock = Semaphore()
    
    def run(self):
        # Wait for XMDS to be initialised and available to us
        while self.xmds == None:
            time.sleep(60)
            
        while self.running:
            if (self.processing):
                pass
            else:
                self.process()
            time.sleep(30)
    
    def process(self):
        self.__lock.acquire()
        self.processing = True
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
        
        if len(self.logE.childNodes) > 0:
            # Get each trace in turn and send it to XMDS
            traceNodes = self.logXml.getElementsByTagName('trace')

            nExceptions = 0
            xml = '<log>'
            nodes = []
            nProcessed = 0
            for trace in traceNodes:
                # Ship the logXml off to XMDS
                if len(nodes) < 10:
                    nProcessed += 1
                    nodes.append(trace)
                    xml += trace.toxml()
                
                if len(nodes) >= 10 or nProcessed == len(traceNodes):
                    try:
                        self.xmds.SubmitLog(xml + "</log>")
                        xml = '<log>'
                        for n in nodes:
                            self.logE.removeChild(n)
                        nodes = []
                    except XMDSException:
                        nExceptions += 1
                        if nExceptions > 4:
                            break
                    except:
                        pass
            
            if len(self.logXml.getElementsByTagName('trace')) > 0:
                # Some logs didn't send
                # Flush to disk    
                # Check the log folder exists:
                try:
                    os.makedirs(config.get('Main','libraryDir') + os.sep + 'log')
                except:
                    pass

                try:
                    try:
                        f = open(config.get('Main','libraryDir') + os.sep + 'log' + os.sep + 'log' + str(time.time()) + '.ready','w')
                        f.write(self.logXml.toprettyxml())
                        self.logXml.unlink()
                        self.logXml = minidom.Document()
                        self.logE = self.logXml.createElement("log")
                        self.logXml.appendChild(self.logE)    
                    finally:
                        f.close()
                except:
                    pass
            else:
                # All the logs send
                # Read in a past log file and append to logE for processing on the next run
                readOne = False
                
                # If this is a flush being called, skip reading in a new file as it will be lost in memory.
                if self.flush:
                    readOne = True
                
                # Check the log folder exists:
                try:
                    os.makedirs(config.get('Main','libraryDir') + os.sep + 'log')
                except:
                    pass
                
                for f in os.listdir(config.get('Main','libraryDir') + os.sep + 'log'):
                    if readOne == False:
                        if fnmatch.fnmatch(f, '*.ready'):
                            try:
                                self.logXml.unlink()
                                self.logXml = minidom.parse(config.get('Main','libraryDir') + os.sep + 'log' + os.sep + f)
                                for n in self.logXml.getElementsByTagName('log'):
                                    self.logE = n
                            except:
                                # File must be invalid. Delete it
                                try:
                                    os.remove(config.get('Main','libraryDir') + os.sep + 'log' + os.sep + f)
                                except:
                                    readOne = False
                                    continue
                                    
                            # Now the file is back in memory, delete it
                            try:
                                os.remove(config.get('Main','libraryDir') + os.sep + 'log' + os.sep + f)
                                readOne = True
                            except:
                                pass
            
        # Deal with stats:
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
        
        if len(self.statsE.childNodes) >= self.statsQueueSize or self.flush: 
            self.flush = False
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
                        f.write(self.statXml.toprettyxml())
                    finally:
                        f.close()
                except:
                    pass
        self.processing = False
        self.__lock.release()
#### Finish Log Classes

#### Download Manager
class XiboFile(object):
    def __init__(self,fileName,targetHash,fileId,fileType,mtime=0):
        self.__path = os.path.join(config.get('Main','libraryDir'),fileName)
        self.__fileName = fileName
        self.md5 = "NOT CALCULATED"
        self.checkTime = 1
        self.fileType = fileType
        self.fileId = fileId

        self.targetHash = targetHash
        self.mtime = mtime
        self.paranoid = config.get('Main','checksumPreviousDownloads')
        if self.paranoid == "true":
            self.update()
            self.paranoid = True
        else:
            self.paranoid = False
            try:
                if os.path.getmtime(self.__path) == self.mtime:
                    self.md5 = self.targetHash
                else:
                    self.update()
            except:
                self.update()
        

    def update(self):
        # Generate MD5
        m = hashlib.md5()
        try:
#            print "*** GENERATING MD5 for file %s" % self.__fileName
            for line in open(self.__path,"rb"):
                m.update(line)    
        except IOError:
#            print "*** IOERROR"
            return False
                    
        self.md5 = m.hexdigest()
        self.mtime = os.path.getmtime(self.__path)
        self.checkTime = time.time()
        return True

    def isExpired(self):
        if self.paranoid:
            return self.checkTime + 3600 < time.time()
        else:
            try:
                tmpMtime = os.path.getmtime(self.__path)
            except:
                return False
            
            return not self.mtime == tmpMtime

    def isValid(self):
        try:
            tmpMtime = os.path.getmtime(self.__path)
        except:
            return False
        return (self.md5 == self.targetHash) and (self.mtime == tmpMtime)
    
    def toTuple(self):
        return (self.__fileName,self.md5,self.targetHash,self.checkTime,self.mtime,self.fileId,self.fileType)

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
        self.offline = config.getboolean('Main','manualUpdate')

        # Store a dictionary of XiboDownloadThread objects so we know
        # which files are downloading and how many download slots
        # there are free
        self.runningDownloads = defaultdict(XiboDownloadThread)

        # How many XiboDownloadThreads should run at once
        self.maxDownloads = 5
        
        # Populate md5Cache
        if config.get('Main','checksumPreviousDownloads') == "false":
            try:
                tmpDoc = minidom.parse(os.path.join(config.get('Main','libraryDir'),'cache.xml'))
                for f in tmpDoc.getElementsByTagName('file'):
                    tmpFileName = str(f.attributes['name'].value)
                    tmpHash = str(f.attributes['md5'].value)
                    tmpMtime = float(f.attributes['mtime'].value)
                    tmpId = int(f.attributes['id'].value)
                    tmpType = str(f.attributes['type'].value)
                    tmpFile = XiboFile(tmpFileName,tmpHash,tmpId,tmpType,tmpMtime)
                    md5Cache[tmpFileName] = tmpFile
            except IOError:
                log.log(0,"warning",_("Could not open cache.xml. Starting with an empty cache"),True)
            except:
                log.log(0,"warning",_("md5Cache file is corrupted. Ignoring."),True)

    def run(self):
        log.log(2,"info",_("New XiboDownloadManager instance started."))
        while (self.running):
            self.interval = 300

            # Find out how long we should wait between updates.
            try:
                self.interval = int(config.get('Main','xmdsUpdateInterval'))
            except:
                # self.interval has been set to a sensible default in this case.
                log.log(0,"warning",_("No XMDS Update Interval specified in your configuration"),True)
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
                log.log(0,"error",_("Error trying to cache RequiredFiles to disk"),True)
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
                log.log(0,"warning",_("XMDS RequiredFiles returned invalid XML"),True)

            # Find the layout node and store it
            if self.doc != None:
                fileNodes = self.doc.getElementsByTagName('file')
                for f in fileNodes:
                    # Does the file exist? Is it the right size?
                    if str(f.attributes['type'].value) == 'media':
                        try:
                            tmpPath = os.path.join(config.get('Main','libraryDir'),str(f.attributes['path'].value))
                            tmpFileName = str(f.attributes['path'].value)
                            tmpSize = long(f.attributes['size'].value)
                            tmpHash = str(f.attributes['md5'].value)
                            tmpType = str(f.attributes['type'].value)
                            try:
                                tmpId = int(f.attributes['id'].value)
                            except:
                                # Layout background images don't come down with IDs
                                # Blame Dan :D
                                tmpId = 0

                            if os.path.isfile(tmpPath) and os.path.getsize(tmpPath) == tmpSize:
                                # File exists and is the right size
                                # See if we checksummed it recently
                                if tmpFileName in md5Cache:
                                    # Check if the md5 cache is old for this file
                                    if md5Cache[tmpFileName].isExpired():
                                        # Update the cache if it is
#                                        print "*** It's 726 updating %s" % tmpFileName
                                        md5Cache[tmpFileName].update()

                                    if not md5Cache[tmpFileName].isValid():
                                        # The hashes don't match.
                                        # Queue for download.
                                        log.log(2,"warning",_("File exists and is the correct size, but the checksum is incorrect. Queueing for download. ") + tmpFileName,True)
                                        self.dlQueue.put((tmpType,tmpFileName,tmpSize,tmpHash,tmpId),False)
                                else:
#                                    print "*** It's 735 and %s isn't in md5Cache" % tmpFileName
                                    tmpFile = XiboFile(tmpFileName,tmpHash,tmpId,tmpType)
                                    md5Cache[tmpFileName] = tmpFile
                                    if not tmpFile.isValid():
                                        # The hashes don't match.
                                        # Queue for download.
                                        log.log(2,"warning",_("File exists and is the correct size, but the checksum is incorrect. Queueing for download. ") + tmpFileName,True)
                                        self.dlQueue.put((tmpType,tmpFileName,tmpSize,tmpHash,tmpId),False)
                            else:
                                # Queue the file for download later.
                                log.log(3,"info",_("File does not exist or is not the correct size. Queueing for download. ") + tmpFileName,True)
                                tmpFile = XiboFile(tmpFileName,tmpHash,tmpId,tmpType)
                                md5Cache[tmpFileName] = tmpFile
                                self.dlQueue.put((tmpType,tmpFileName,tmpSize,tmpHash,tmpId),False)
                        except:
                            # TODO: Blacklist the media item.
                            log.log(0,"error",_("RequiredFiles XML error: File type=media has no path attribute or no size attribute. Blacklisting."),True)

                        log.log(5,"audit",_("File " + tmpFileName + " is valid."))
                        
                    elif str(f.attributes['type'].value) == 'layout':
                    # It's a Layout node.
                        try:
                            tmpPath = os.path.join(config.get('Main','libraryDir'),str(f.attributes['path'].value) + '.xlf')
                            tmpFileName = str(f.attributes['path'].value) + '.xlf'
                            tmpHash = str(f.attributes['md5'].value)
                            tmpType = str(f.attributes['type'].value)
                            tmpId = int(f.attributes['id'].value)

                            if os.path.isfile(tmpPath):
                                # File exists
                                # See if we checksummed it recently
                                if tmpFileName in md5Cache:
                                    # Check if the md5 cache is old for this file
                                    if md5Cache[tmpFileName].isExpired():
                                        # Update the cache if it is
                                        md5Cache[tmpFileName].update()
                                    
                                    # The file is in cache, but has changed hash on the server
                                    if md5Cache[tmpFileName].targetHash != tmpHash:
                                        md5Cache[tmpFileName].targetHash = tmpHash
                                        md5Cache[tmpFileName].update()

                                    if md5Cache[tmpFileName].md5 != tmpHash:
                                        # The hashes don't match.
                                        # Queue for download.
                                        log.log(2,"warning",_("File exists and is the correct size, but the checksum is incorrect. Queueing for download. ") + tmpFileName,True)
                                        self.dlQueue.put((tmpType,tmpFileName,0,tmpHash,tmpId),False)
                                else:
                                    tmpFile = XiboFile(tmpFileName,tmpHash,tmpId,tmpType)
                                    md5Cache[tmpFileName] = tmpFile
                                    if not tmpFile.isValid():
                                        # The hashes don't match.
                                        # Queue for download.
                                        log.log(2,"warning",_("File exists and is the correct size, but the checksum is incorrect. Queueing for download. ") + tmpFileName,True)
                                        self.dlQueue.put((tmpType,tmpFileName,0,tmpHash,tmpId),False)
                            else:
                                # Queue the file for download later.
                                log.log(3,"info",_("File does not exist. Queueing for download. ") + tmpFileName,True)
                                tmpFile = XiboFile(tmpFileName,tmpHash,tmpId,tmpType)
                                md5Cache[tmpFileName] = tmpFile
                                self.dlQueue.put((tmpType,tmpFileName,0,tmpHash,tmpId),False)
                        except:
                            # TODO: Blacklist the media item.
                            log.log(0,"error",_("RequiredFiles XML error: File type=layout has no path attribute or no hash attribute. Blacklisting."),True)
                    elif str(f.attributes['type'].value) == 'blacklist':
                        # It's a Blacklist node
                        #log.log(5,"info","Blacklist File Node found!")
                        # TODO: Do something with the blacklist
                        pass
                    else:
                        # Unknown node. Ignore
                        pass

                fileNodes = None
            # End If self.doc != None

            self.updateInfo()
            self.updateMediaInventory()

            # Loop over the queue and download as required
            try:
                # Throttle this to a maximum number of dl threads.
                while True:
                    tmpType, tmpFileName, tmpSize, tmpHash, tmpId = self.dlQueue.get(False)

                    if config.get('Main','manualUpdate') == 'true':
                        log.lights('offlineUpdate','start')

                    # Check if the file is downloading already
                    if not tmpFileName in self.runningDownloads:
                        # Make a download thread and actually download the file.
                        # Add the running thread to the self.runningDownloads dictionary
                        self.runningDownloads[tmpFileName] = XiboDownloadThread(self,tmpType,tmpFileName,tmpSize,tmpHash,tmpId)
                        log.updateRunningDownloads(len(self.runningDownloads))

                        if self.offline:
                            # If we're running offline, block until completed.
                            self.runningDownloads[tmpFileName].run()
                        else:
                            self.runningDownloads[tmpFileName].start()

                    while len(self.runningDownloads) >= (self.maxDownloads - 1):
                        # There are no download thread slots free
                        # Sleep for 5 seconds and try again.
                        log.log(3,"info",_("All download slots filled. Waiting for a download slot to become free"))
                        time.sleep(5)
                    # End While

            except Queue.Empty:
                # Used to exit the above while once all items are downloaded.
                pass
            
            cacheXml = minidom.Document()
            cacheXmlRoot = cacheXml.createElement("cache")
            cacheXml.appendChild(cacheXmlRoot)

            # Loop over the MD5 hash cache and remove any entries older than 1 hour
            try:
                for tmpFileName, tmpFile in md5Cache.iteritems():
                    if tmpFile.isExpired() and (not tmpFileName in self.runningDownloads):
                        del md5Cache[tmpFileName]
                        
                    # Prepare to cache out to file
                    tmpFileInfo = tmpFile.toTuple()
                    tmpNode = cacheXml.createElement("file")
                    tmpNode.setAttribute("name",tmpFileName)
                    tmpNode.setAttribute("md5",tmpFileInfo[2])
                    tmpNode.setAttribute("mtime",str(tmpFileInfo[4]))
                    tmpNode.setAttribute("id",str(tmpFileInfo[5]))
                    tmpNode.setAttribute("type",str(tmpFileInfo[6]))
                    cacheXmlRoot.appendChild(tmpNode)
            except RuntimeError:
                # Happens when we delete an item from the cache it would seem.
                pass

            # Write the cache out to disk
            try:
                f = open(os.path.join(config.get('Main','libraryDir'),'cache.xml'),'w')
                f.write(cacheXml.toprettyxml())
                f.close()
            except IOError:
                log.log(0,"error",_("Unable to write cache.xml"),True)
                
            # Force the cache to unlink and recover the RAM associated with it    
            cacheXml.unlink()
   
            # End Loop

            # Update the infoscreen.
            self.updateInfo()
            self.updateMediaInventory()
            
            log.log(5,"audit",_("There are ") + str(threading.activeCount()) + _(" running threads."))

            if config.getboolean('Main','manualUpdate'):
                time.sleep(5)
                log.lights('offlineUpdate','finish')
            else:
                log.log(3,"audit",_("XiboDownloadManager: Sleeping") + " " + str(self.interval) + " " + _("seconds"))
                self.p.enqueue('timer',(int(self.interval) * 1000,self.collect))

            self.__lock.acquire()
        # End While
    
    def collect(self):
        if len(self.runningDownloads) == 0:
            self.__lock.release()

    def dlThreadCompleteNotify(self,tmpFileName):
        # Download thread completed. Log and remove from
        # self.runningDownloads
        log.log(3,"info",_("Download thread completed for ") + tmpFileName, True)
        del self.runningDownloads[tmpFileName]
        log.updateRunningDownloads(len(self.runningDownloads))
        
        # Update the infoscreen
        self.updateInfo()
        self.updateMediaInventory()

    def updateInfo(self):
        # Update the info screen with information about the media
        # and it's status
        infoStr = ""
        
        for tmpFileName, tmpFile in md5Cache.iteritems():
            if tmpFile.isValid():
                infoStr += tmpFileName + ", "
            else:
                infoStr += "<i>" + tmpFileName + "</i>, "
        
        log.updateMedia(infoStr)

    def updateMediaInventory(self):
        # Silently return if in full offline mode
        if config.getboolean('Main','manualUpdate'):
            return

        if not config.getboolean('Main','mediaInventory'):
            return

        # Get current md5Cache and send it back to the server
        inventoryXml = minidom.Document()
        inventoryXmlRoot = inventoryXml.createElement("files")
        inventoryXml.appendChild(inventoryXmlRoot)

        # Loop over the MD5 hash cache and build the inventory
        try:
            for tmpFileName, tmpFile in md5Cache.iteritems():
                tmpFileInfo = tmpFile.toTuple()
                tmpNode = inventoryXml.createElement("file")
                tmpNode.setAttribute("md5",tmpFileInfo[1])

                # Convert unix timestamp to ISO format
                tmpDt = datetime.datetime.fromtimestamp(tmpFileInfo[3])
                tmpDt = tmpDt.strftime("%Y-%m-%d %H:%M:%S")

                tmpNode.setAttribute("lastChecked",tmpDt)
                tmpNode.setAttribute("id",str(tmpFileInfo[5]))
                tmpNode.setAttribute("type",str(tmpFileInfo[6]))

                if tmpFile.isValid():
                    tmpNode.setAttribute("complete","1")
                else:
                    tmpNode.setAttribute("complete","0")

                inventoryXmlRoot.appendChild(tmpNode)
        except:
            log.log(0,'error',_('updateMediaInventory: Unknown error building inventoryXml'))

        # Send via XMDS
        try:
            self.xmds.MediaInventory(inventoryXml.toprettyxml())
        except XMDSException:
            log.log(1,'error',_('Unable to send mediaInventory to the server via XMDS.'))

        inventoryXml.unlink()

class XiboDownloadThread(Thread):
    def __init__(self,parent,tmpType,tmpFileName,tmpSize,tmpHash,tmpId):
        Thread.__init__(self)
        self.tmpType = tmpType
        self.tmpId = tmpId
        self.tmpFileName = tmpFileName
        self.tmpPath = os.path.join(config.get('Main','libraryDir'),self.tmpFileName)
        self.tmpSize = tmpSize
        self.tmpHash = tmpHash
        self.parent = parent
        self.offset = long(0)
        self.chunk = 512000
        
        # Server versions prior to 1.0.5 send an invalid md5sum for layouts that require
        # the client to add a newline character to the returned layout to make it validate
        # Should the client assume the server is pre-1.0.5?
        try:
            self.backCompat = config.get('Main','backCompatLayoutChecksums')
            if self.backCompat == "false":
                self.backCompat = False
            else:
                self.backCompat = True
        except:
            self.backCompat = False

    def run(self):
        # Manage downloading the appropriate type of file:
        if self.tmpType == "media":
            self.downloadMedia()
        elif self.tmpType == "layout":
            self.downloadLayout()

        # Let the DownloadManager know we're complete
        self.parent.dlThreadCompleteNotify(self.tmpFileName)

    def downloadMedia(self):
        # Actually download the Media file
        finished = False
        tries = 0

        if os.path.isfile(self.tmpPath):
            try:
                os.remove(self.tmpPath)
            except:
                log.log(0,"error",_("Unable to delete file: ") + self.tmpPath, True)
                return

        fh = None
        try:
            fh = open(self.tmpPath, 'wb')
        except:
            log.log(0,"error",_("Unable to write file: ") + self.tmpPath, True)
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
                    response = self.parent.xmds.GetFile(self.tmpFileName,self.tmpType,self.offset,self.chunk)
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
                except ValueError:
                    finished = True
                    break

            # End while offset<tmpSize
            try:
                fh.close()
            except:
                # TODO: Do something sensible
                pass

            # Check size/md5 here
            tmpFile = XiboFile(self.tmpFileName,self.tmpHash,self.tmpId,self.tmpType)
            if tmpFile.isValid():
                finished = True
                md5Cache[self.tmpFileName] = tmpFile
        # End while

    def downloadLayout(self):
        # Actually download the Layout file
        finished = False
        tries = 0

        if os.path.isfile(self.tmpPath):
            try:
                os.remove(self.tmpPath)
            except:
                log.log(0,"error",_("Unable to delete file: ") + self.tmpPath, True)
                return

        while tries < 5 and not finished:
            tries = tries + 1

            fh = None
            try:
                fh = open(self.tmpPath, 'wb')
            except:
                log.log(0,"error",_("Unable to write file: ") + self.tmpPath, True)
                return

            try:
                response = self.parent.xmds.GetFile(self.tmpFileName,self.tmpType,0,0)
                if self.backCompat:
                    fh.write(response + '\n')
                else:
                    fh.write(response)
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

            # Check size/md5 here
            tmpFile = XiboFile(self.tmpFileName,self.tmpHash,self.tmpId,self.tmpType)
            if tmpFile.isValid():
                finished = True
                md5Cache[self.tmpFileName] = tmpFile
            else:
                log.log(4,"warning",_("File completed downloading but MD5 did not match.") + self.tmpFileName, True)
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
        log.log(6,"info",_("%s XiboLayoutManager instance running.") % self.l.layoutID)

        # Add a DIV to contain the whole layout (for transitioning whole layouts in to one another)
        # TODO: Take account of the zindex parameter for transitions. Should this layout sit on top or underneath?
        # Ensure that the layoutNodeName is unique on the player (incase we have to transition to ourself)
        self.layoutNodeName = 'L' + str(self.l.layoutID) + self.layoutNodeNameExt

        # Create the XML that will render the layoutNode.
        tmpXML = '<div id="' + self.layoutNodeName + '" width="' + str(self.l.sWidth) + '" height="' + str(self.l.sHeight) + '" x="' + str(self.l.offsetX) + '" y="' + str(self.l.offsetY) + '" opacity="' + str(self.opacity) + '" crop="False" />'
        self.p.enqueue('add',(tmpXML,'screen'))

        # Add a ColorNode and maybe ImageNode to the layout div to draw the background

        # This code will work with libavg > 0.8.x
        try:
            tmpXML = '<rect fillopacity="1" fillcolor="%s" color="%s" size="(%d,%d)" id="bgColor%s" />' % (self.l.backgroundColour.strip("#"),self.l.backgroundColour.strip("#"),self.l.sWidth,self.l.sHeight,self.layoutNodeNameExt)
            self.p.enqueue('add',(tmpXML,self.layoutNodeName))
        except AttributeError:
            # The background colour isn't set for the layout.
            # This is likely to be bad news as the XLF is already invalid.
            # Log this, sleep and then load a different layout.
            log.log(0,'error',_("Layout %s is invalid or corrupt. No background colour specified in the XLF. Skipping.") % self.l.layoutID)
            time.sleep(5)
            self.parent.nextLayout()
            return

        if self.l.backgroundImage != None:
            
            # If there's a backgroud image, scale it to preserve texture memory
            # If lowTextureMemory is true (eg on Intel Graphics Cards), use Thumbnail to
            # produce much smaller image sizes.

            if config.get('Main','lowTextureMemory') == "true":
                w = int((self.l.sWidth + 1) * 1.1)
                h = int((self.l.sHeight + 1) * 1.1)
            else:
                w = int(self.l.sWidth + 1)
                h = int(self.l.sHeight + 1)
                
            fName = os.path.join(config.get('Main','libraryDir'),self.l.backgroundImage)
            thumb = os.path.join(config.get('Main','libraryDir'),'scaled',self.l.backgroundImage) + "-%dx%d" % (w,h)

            if not os.path.exists(thumb) or (os.path.getmtime(thumb) < os.path.getmtime(fName)):
                log.log(3,'info',_("%s: Resizing image %s to %dx%d") % (self.layoutNodeName,fName,w,h))
                image = PIL.Image.open(fName)
                
                if config.get('Main','lowTextureMemory') == "true":
                    image.thumbnail((w,h),PIL.Image.ANTIALIAS)
                else:
                    image.resize((w,h),PIL.Image.ANTIALIAS)
                    
                image.save(thumb, image.format)
                del image
            
            tmpXML = str('<image width="%d" height="%d" id="bg%s" opacity="1.0" />' % (self.l.sWidth,self.l.sHeight,self.layoutNodeNameExt))
            self.p.enqueue('add',(tmpXML,self.layoutNodeName))
            
            bitmap = avg.Bitmap(thumb)
            self.p.enqueue('setBitmap',("bg%s" % self.layoutNodeNameExt, bitmap))

        # Break layout in to regions
        # Spawn a region manager for each region and then start them all running
        # Log each region in an array for checking later.
        for cn in self.l.children():
            if cn.nodeType == cn.ELEMENT_NODE and cn.localName == "region":
                # Create a new Region Manager Thread and kick it running.
                # Pass in cn since it contains the XML for the whole region

                # TODO: Instead of starting here, we need to sort the regions array by zindex attribute
                # then start in ascending order to ensure rendering happens in layers correctly.
                tmpRegion = XiboRegionManager(self, self.p, self.layoutNodeName, self.layoutNodeNameExt, cn)
                log.log(2,"info",_("XiboLayoutManager: run() -> Starting new XiboRegionManager."))
                tmpRegion.start()
                # Store a reference to the region so we can talk to it later
                self.regions.append(tmpRegion)

    def regionElapsed(self):
        log.log(2,"info",_("%s Region elapsed. Checking if layout has elapsed") % self.layoutNodeName)

        allExpired = True
        for i in self.regions:
            if i.regionExpired == False:
                log.log(3,"info",_("%s Region " + i.regionNodeName + " has not expired. Waiting") % self.layoutNodeName)
                allExpired = False
                return False

        self.__regionLock.acquire()

        if allExpired and not self.expiring:
            log.log(2,"info",_("%s All regions have expired. Marking layout as expired") % self.layoutNodeName, True)
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
        log.log(2,"info",_("%s Region disposed. Checking if all regions have disposed") % self.layoutNodeName)

        allExpired = True
        for i in self.regions:
            if i.disposed == False:
                log.log(3,"info",_("%s Region %s has not disposed. Waiting") % (self.layoutNodeName,i.regionNodeName))
                allExpired = False

        self.__regionDisposeLock.acquire()
        if allExpired == True and not self.nextLayoutTriggered:
            log.log(2,"info",_("%s All regions have disposed. Marking layout as disposed") % self.layoutNodeName, True)
            self.layoutDisposed = True

            if self.hold:
                log.log(2,"info",_("Holding the splash screen until we're told otherwise"), True)
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
        self.regionId = None

        # Calculate the region ID name
        try:
            self.regionNodeName = "R" + str(self.regionNode.attributes['id'].value) + self.regionNodeNameExt
            self.regionId = str(self.regionNode.attributes['id'].value)
        except KeyError:
            log.log(1,"error",_("Region XLF is invalid. Missing required id attribute"), True)
            self.regionExpired = True
            self.parent.regionElapsed()
            return


        # Calculate the region width
        try:
            self.width = float(self.regionNode.attributes['width'].value) * parent.l.scaleFactor
        except KeyError:
            log.log(1,"error",_("Region XLF is invalid. Missing required width attribute"), True)
            self.regionExpired = True
            self.parent.regionElapsed()
            return

        # Calculate the region height
        try:
            self.height =  float(self.regionNode.attributes['height'].value) * parent.l.scaleFactor
        except KeyError:
            log.log(1,"error",_("Region XLF is invalid. Missing required height attribute"), True)
            self.regionExpired = True
            self.parent.regionElapsed()
            return

        # Calculate the region top
        try:
            self.top = float(self.regionNode.attributes['top'].value) * parent.l.scaleFactor
        except KeyError:
            log.log(1,"error",_("Region XLF is invalid. Missing required top attribute"), True)
            self.regionExpired = True
            self.parent.regionElapsed()
            return

        # Calculate the region left
        try:
            self.left = float(self.regionNode.attributes['left'].value) * parent.l.scaleFactor
        except KeyError:
            log.log(1,"error",_("Region XLF is invalid. Missing required left attribute"))
            self.regionExpired = True
            self.parent.regionElapsed()
            return

        # Get region zindex
        try:
            self.zindex = int(float(self.regionNode.attributes['zindex'].value))
        except KeyError:
            self.zindex = 1
        
        # Create a div for the region and add it
        tmpXML = '<div id="' + self.regionNodeName + '" width="' + str(self.width) + '" height="' + str(self.height) + '" x="' + str(self.left) + '" y="' + str(self.top) + '" opacity="1.0" crop="False" />'
        self.p.enqueue('add',(tmpXML,self.layoutNodeName))

    def run(self):
        self.lock.acquire()
        self.tLock.acquire()
        log.log(3,"info",_("New XiboRegionManager instance running for region:") + self.regionNodeName)

        #  * Iterate through the media items
        #  -> For each media, display on screen and set a timer to cause the next item to be shown
        #  -> attempt to acquire self.lock - which will block this thread. We will be woken by the callback
        #     to next() by the libavg player.
        #  * When all items complete, mark region complete by setting regionExpired = True and calling parent.regionElapsed()
        mediaCount = 0

        while self.disposed == False and self.oneItemOnly == False and self.disposing == False:
            for cn in self.regionNode.childNodes:
                if cn.nodeType == cn.ELEMENT_NODE and cn.localName == "media":
                    log.log(3,"info","%s: Moving to next Media item" % self.regionNodeName)
                    mediaCount = mediaCount + 1
                    if self.disposed == False and self.disposing == False:
                        type = str(cn.attributes['type'].value)
                        type = type[0:1].upper() + type[1:]
                        log.log(4,"info","%s: Media is of type: %s" % (self.regionNodeName,type))
                        try:
                            import plugins.media
                            __import__("plugins.media." + type + "Media",None,None,[''])
                            self.currentMedia = eval("plugins.media." + type + "Media." + type + "Media")(log,config,self,self.p,cn)

                            # Apply (multiple or none) media effects here
                            import plugins.effects
                            tmpEffects = []
                            for cn in self.currentMedia.effects:
                                eType = str(cn.attributes['type'].value)
                                eType = eType[0:1].upper() + eType[1:]
                                __import__("plugins.effects." + eType + "Effect",None,None,[''])
                                tmpE = eval("plugins.effects." + eType + "Effect." + eType + "Effect")(log,self.p,self.currentMedia.mediaNodeName,cn)
                                tmpEffects.append(tmpE)

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

                            log.log(3,"info",self.regionNodeName + ": " + _("Beginning transitions: " + str(trans)))
                            # The two transitions match. Let one plugin handle both.
                            if (trans[0] == trans[1]) and trans[0] != "":
                                self.currentMedia.add()
                                self.currentMedia.start()
                                for e in tmpEffects:
                                    e.start()
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
                                    for e in tmpEffects:
                                        e.start()
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
                                    for e in tmpEffects:
                                        e.start()
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
                            log.log(0,"error","Missing media plugin for media type " + type + ": " + str(detail), True)
                            # TODO: Do something with this layout? Blacklist?
                            self.lock.release()

            # If there's no items, pause for a while to allow other RegionManagers to get up and running.
            if mediaCount == 0:
                self.oneItemOnly = True
                log.log(3,"info",_("Region has no media: ") + self.regionNodeName)
                time.sleep(2)
                
            self.regionExpired = True
            print str(self.regionNodeName) + " has expired"
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
                log.log(3,"error",self.regionNodeName + ": Unable to import requested Transition plugin. " + str(detail), True)
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
    def __init__(self,layoutID,isDefault):
        self.layoutID = layoutID
        self.isDefault = isDefault
        self.__mtime = 0
        self.schedule = []
        self.__setup()
        
    def __setup(self):
        self.builtWithNoXLF = False
        self.layoutNode = None
        self.iter = None

        if not int(config.get('Main','vwidth')) == 0:
            self.playerWidth = int(config.get('Main','vwidth'))
            self.playerHeight = int(config.get('Main','vheight'))
        else:
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
        self.scheduleCheck = False
        self.pluginCheck = True
        
        if self.layoutID == "0":
            try:
                if not os.path.isfile(os.path.join(config.get('Main','libraryDir'),'0.xlf')):
                    import shutil
                    shutil.copy(os.path.join('resources','0.xlf'),config.get('Main','libraryDir'))
                if not os.path.isfile(os.path.join(config.get('Main','libraryDir'),'splash.jpg')):
                    import shutil
                    shutil.copy(os.path.join('resources','splash.jpg'),config.get('Main','libraryDir'))
            except IOError:
                log.log(0,"error",_("Unable to write to libraryDir %s") % config.get('Main','libraryDir'), True)

        # Read XLF from file (if it exists)
        # Set builtWithNoXLF = True if it doesn't
        try:
            log.log(3,"info",_("Loading layout ID") + " " + self.layoutID + " " + _("from file") + " " + config.get('Main','libraryDir') + os.sep + self.layoutID + '.xlf')
            self.doc = minidom.parse(config.get('Main','libraryDir') + os.sep + self.layoutID + '.xlf')

            self.__mtime = os.path.getmtime(config.get('Main','libraryDir') + os.sep + self.layoutID + '.xlf')

            # Find the layout node and store it
            for e in self.doc.childNodes:
                if e.nodeType == e.ELEMENT_NODE and e.localName == "layout":
                    self.layoutNode = e

            # Check the layout's schemaVersion matches the version this client understands
            try:
                xlfSchemaVersion = int(self.layoutNode.attributes['schemaVersion'].value)
            except KeyError:
                log.log(1,"error",_("Layout has no schemaVersion attribute and cannot be shown by this client"), True)
                self.builtWithNoXLF = True
                self.schemaCheck = False
                return

            if xlfSchemaVersion != schemaVersion:
                # Layout has incorrect schemaVersion.
                # Set the flag so the scheduler doesn't present this to the display
                log.log(1,"error",_("Layout has incorrect schemaVersion attribute and cannot be shown by this client.") + " " + str(xlfSchemaVersion) + " != " + str(schemaVersion), True)
                self.schemaCheck = False
                self.builtWithNoXLF = True
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
                log.log(1,"error",_("Layout XLF is invalid. Missing required attributes"), True)

            try:
                self.backgroundImage = self.layoutNode.attributes['background'].value
                if self.backgroundImage == "":
                    self.backgroundImage = None
            except KeyError:
                # Optional attributes, so pass on error.
                self.backgroundImage = None
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
        self.mediaNodes = self.doc.getElementsByTagName('media')

        # Iterate over the media nodes and extract path names
        # Make a media object minus its Player (to prevent any accidents!) and ask it
        # what media it needs to run. This allows us to be extensible.
        for mn in self.mediaNodes:
            type = str(mn.attributes['type'].value)
            type = type[0:1].upper() + type[1:]
            try:
                import plugins.media
                __import__("plugins.media." + type + "Media",None,None,[''])
                tmpMedia = eval("plugins.media." + type + "Media." + type + "Media")(log,config,None,None,mn)
            except IOError:
                self.pluginCheck = False
                log.log(0,"error",_("Plugin missing for media in layout ") + self.layoutID)
                return
            self.media = self.media + tmpMedia.requiredFiles()

        # Also make sure we have the background (if the layout uses one)
        if self.backgroundImage != None:
            self.media = self.media + [self.backgroundImage]
        
        # Find all the tag nodes
        tagNodes = self.doc.getElementsByTagName('tag')
        
        # Iterate over the tag nodes and extract the tags
        for tag in tagNodes:
            try:
                self.tags.append(str(tag.firstChild.nodeValue))
            except AttributeError:
                pass
        
        log.log(3,"info","Layout " + str(self.layoutID) + " has tags: " + str(self.tags)) 

    def canRun(self):
        # See if the layout file changed underneath us
        try:
            if self.__mtime != os.path.getmtime(config.get('Main','libraryDir') + os.sep + self.layoutID + '.xlf'):
                # It has. Force a reload
                self.builtWithNoXLF = True
        except:
            return False

        # See if we were built with no XLF
        # If we were, attempt to set ourselves up
        # Otherwise return False
        if self.builtWithNoXLF:
            self.__setup()
            if self.builtWithNoXLF:
                return False
        
        self.mediaCheck = True
        self.scheduleCheck = False
        
        if len(self.mediaNodes) < 1:
            log.log(3,"warn",_("Layout ") + self.layoutID + _(" cannot run because layout has no media nodes."), True)
            self.mediaCheck = False

        # Loop through all the media items in the layout
        # Check them against md5Cache
        for tmpFileName in self.media:
            tmpPath = os.path.join(config.get('Main','libraryDir'),tmpFileName)
            if tmpFileName in md5Cache:
                # Check if the md5 cache is old for this file
                try:
                    if not md5Cache[tmpFileName].isValid():
                        self.mediaCheck = False
                        log.log(3,"warn",_("Layout ") + self.layoutID + _(" cannot run because MD5 is incorrect on ") + tmpFileName, True)

                    if not os.path.isfile(tmpPath):
                        self.mediaCheck = False
                        log.log(0,"error",_("Layout ") + self.layoutID + _(" cannot run because file is missing: ") + tmpFileName, True)
                except:
                    self.mediaCheck = False
                    log.log(0,"error",_("Layout ") + self.layoutID + _(" cannot run because an exception was thrown.") + tmpFileName, True)
            else:
                self.mediaCheck = False
                log.log(3,"info",_("Layout ") + self.layoutID + _(" cannot run because file is missing from the md5Cache: ") + tmpFileName, True)

        # See if the item is in a scheduled window to run
        for sc in self.schedule:
            try:
                fromDt = time.mktime(time.strptime(sc[0], "%Y-%m-%d %H:%M:%S"))
            except OverflowError:
                log.log(0, 'error', _("Layout %s has an invalid schedule start time. Using 00:00:00 UTC on 1 January 1970") % self.layoutID)
                fromtDt = 0
            except ValueError:
                log.log(0, 'error', _("Layout %s has an invalid schedule start time. Using 00:00:00 UTC on 1 January 1970") % self.layoutID)
                fromtDt = 0

            try:
                toDt = time.mktime(time.strptime(sc[1], "%Y-%m-%d %H:%M:%S"))
            except OverflowError:
                log.log(0, 'error', _("Layout %s has an invalid schedule finish time. Using 00:00:00 UTC on 19 January 2038") % self.layoutID)
                toDt = 2147472000
            except ValueError:
                log.log(0, 'error', _("Layout %s has an invalid schedule finish time. Using 00:00:00 UTC on 19 January 2038") % self.layoutID)
                toDt = 2147472000

            priority = sc[2]
            now = time.time()
            
            # Check if we're in the window. If fromDt > toDt then we've got the
            # default layout (which is essentially an invalid schedule).
            if ((now > fromDt) and (now < toDt)) or fromDt > toDt:
                self.scheduleCheck = True
       
        log.log(3,"info",_("Layout ") + self.layoutID + " canRun(): schema-" + str(self.schemaCheck) + " media-" + str(self.mediaCheck) + " schedule-" + str(self.scheduleCheck) + " plugin-" + str(self.pluginCheck) + " default-" + str(self.isDefault))
        return self.schemaCheck and self.mediaCheck and (self.scheduleCheck or self.isDefault) and self.pluginCheck

    def resetSchedule(self):
        log.log(3, "info", _("Reset schedule information for layout %s") % self.layoutID)
        self.schedule=[]

    def addSchedule(self,fromDt,toDt,priority):
        log.log(3,"info",_("Added schdule information for layout %s: f:%s t:%s p:%d") % (self.layoutID,fromDt,toDt,priority))
        self.schedule.append((fromDt,toDt,priority))

    def isPriority(self):
        # Check through the schedule and see if we're priority at the moment.
        for sc in self.schedule:
            try:
                fromDt = time.mktime(time.strptime(sc[0], "%Y-%m-%d %H:%M:%S"))
            except OverflowError:
                log.log(0, 'error', _("Layout %s has an invalid schedule start time. Using 00:00:00 UTC on 1 January 1970") % self.layoutID)
                fromtDt = 0
            except ValueError:
                log.log(0, 'error', _("Layout %s has an invalid schedule start time. Using 00:00:00 UTC on 1 January 1970") % self.layoutID)
                fromtDt = 0

            try:
                toDt = time.mktime(time.strptime(sc[1], "%Y-%m-%d %H:%M:%S"))
            except OverflowError:
                log.log(0, 'error', _("Layout %s has an invalid schedule finish time. Using 00:00:00 UTC on 19 January 2038") % self.layoutID)
                toDt = 2147472000
            except ValueError:
                log.log(0, 'error', _("Layout %s has an invalid schedule finish time. Using 00:00:00 UTC on 19 January 2038") % self.layoutID)
                toDt = 2147472000

            priority = sc[2]
            now = time.time()
            
            # Check if we're in the window. If fromDt > toDt then we've got the
            # default layout (which is essentially an invalid schedule).
            if (now > fromDt) and (now < toDt):
                if priority == 1:
                    return True

        return False

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

        layout = XiboLayout(self.layoutList[self.layoutIndex],False)
        self.layoutIndex = self.layoutIndex + 1

        if self.layoutIndex == len(self.layoutList):
            self.layoutIndex = 0

        if layout.canRun() == False:
            log.log(3,"info",_("DummyScheduler: nextLayout() -> ") + str(layout.layoutID) + _(" is not ready to run."))
            if len(self.layoutList) > 1:
                return self.nextLayout()
            else:
                return XiboLayout("0",False)
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
        self.__defaultLayout = None
        
        self.validTag = "default"

        try:
            self.liftEnabled = config.get('Lift','enabled')
            if self.liftEnabled == "false":
                self.liftEnabled = False
                log.log(3,"audit",_("Disabling lift functionality in XMDSScheduler"))
            else:
                self.liftEnabled = True
                log.log(3,"audit",_("Enabling lift functionality in XMDSScheduler"))
        except:
            self.liftEnabled = False
            log.log(3,"error",_("Lift->enabled not defined in configuration. Disabling lift functionality in XMDSScheduler"))
        

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
                log.log(0,"warning",_("XMDS Schedule threw an exception"))
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
            
            # Process the received schedule
            # If the schedule hasn't changed, do nothing.
            if self.previousSchedule != schedule:
                self.previousSchedule = schedule
                doc = minidom.parseString(schedule)
                tmpLayouts = doc.getElementsByTagName('layout')
                defaultLayout = doc.getElementsByTagName('default')

                # Parse out the default layout and update if appropriate
                for l in defaultLayout:
                    layoutID = str(l.attributes['file'].value)

                    try:
                        if self.__defaultLayout.layoutID != layoutID:
                            self.__defaultLayout = XiboLayout(layoutID,True)
                    except:
                        self.__defaultLayout = XiboLayout(layoutID,True)
            
                newLayouts = []
                for l in tmpLayouts:
                    layoutID = str(l.attributes['file'].value)
                    layoutFromDT = str(l.attributes['fromdt'].value)
                    layoutToDT = str(l.attributes['todt'].value)
                    layoutPriority = int(l.attributes['priority'].value)
                    flag = True
                    
                    # If the layout already exists, add this schedule to it
                    for g in newLayouts:
                        if g.layoutID == layoutID:
                            # Append Schedule
                            g.addSchedule(layoutFromDT,layoutToDT,layoutPriority)
                            flag = False
                    
                    # The layout doesn't exist, add it and add a schedule for it
                    if flag:
                        tmpLayout = XiboLayout(layoutID,False)
                        tmpLayout.addSchedule(layoutFromDT,layoutToDT,layoutPriority)
                        newLayouts.append(tmpLayout)
                        scheduleText += str(layoutID) + ', '
                # End for l in tmpLayouts
                        
                # Swap the newLayouts array in to the live scheduler
                self.__lock.acquire()
                self.__layouts = newLayouts
                self.__lock.release()
                    
                log.updateSchedule(scheduleText)
            # End if previousSchedule != schedule
            
            if config.getboolean('Main','manualUpdate'):
                pass
            else:
                log.log(3,"info",_("XmdsScheduler: Sleeping") + " " + str(self.interval) + " " + _("seconds"))
                self.p.enqueue('timer',(int(self.interval) * 1000,self.collect))

            self.__collectLock.acquire()
        # End while self.running
    
    def collect(self):
        self.__collectLock.release()

    def __len__(self):
        log.log(8,'audit',_('There are %s layouts in the scheduler.') % len(self.__layouts))
        return len(self.__layouts)

    def nextLayout(self):
        "Return the next valid layout"

        log.log(8,'audit',_('nextLayout: IN'))        
        # If there are no possible layouts then return the default or splash screen straight away.
        if len(self) == 0:
            log.log(8,'audit',_('No layouts available.'))
            try:
                if self.__defaultLayout.canRun():
                    log.log(8,'audit',_('Default layout can run.'))
                    log.updateNowPlaying(str(self.__defaultLayout.layoutID) + " (Default)")
                    return self.__defaultLayout
                else:
                    log.log(8,'audit',_('Default layout cannot run and there are no other layouts. Loading Splash Screen'))
                    log.updateNowPlaying("Splash Screen")
                    return XiboLayout('0',False)
            except:
                log.log(8,'audit',_('Exception thrown checking default layout. Loading Splash Screen.'))
                log.updateNowPlaying("Splash Screen")
                return XiboLayout('0',False)
        
        # Consider each possible layout and see if it can run
        # Lock out the scheduler while we do this so that the
        # maths doesn't go horribly wrong!
        log.log(8,'audit',_('Attempting to acquire scheduler layout lock.'))
        self.__lock.acquire()
        log.log(8,'audit',_('Scheduler layout lock acquired.'))

        # Check if any layout is a priorty.
        thereIsPriority = False
        for l in self.__layouts:
            if l.isPriority():
                log.log(8,'audit',_('There are layouts with priority.'))
                thereIsPriority = True

        count = 0
        while count < len(self):
            self.__pointer = (self.__pointer + 1) % len(self)
            tmpLayout = self.__layouts[self.__pointer]

            log.log(8,'audit',_('Checking layout schedule ID %s.') % self.__pointer)
            
            if self.liftEnabled:
                if thereIsPriority:
                    log.log(8,'audit',_('Lift is enabled and there is a priority layout.'))
                    if tmpLayout.canRun() and tmpLayout.isPriority() and self.validTag in tmpLayout.tags:
                        log.updateNowPlaying(str(tmpLayout.layoutID) + " (P)")
                        log.log(8,'audit',_('Releasing scheduler layout lock.'))
                        self.__lock.release()
                        return tmpLayout
                    else:
                        log.log(8,'audit',_('Trying next layout.'))
                        count = count + 1
                else:
                    log.log(8,'audit',_('Lift is enabled and there are no priority layouts.'))
                    if tmpLayout.canRun() and self.validTag in tmpLayout.tags:
                        log.updateNowPlaying(str(tmpLayout.layoutID))
                        log.log(8,'audit',_('Releasing scheduler layout lock.'))
                        self.__lock.release()
                        return tmpLayout
                    else:
                        log.log(8,'audit',_('Trying next layout.'))
                        count = count + 1
            else:
                if thereIsPriority:
                    if tmpLayout.canRun() and tmpLayout.isPriority():
                        log.updateNowPlaying(str(tmpLayout.layoutID) + " (P)")
                        log.log(8,'audit',_('Releasing scheduler layout lock.'))
                        self.__lock.release()
                        return tmpLayout
                    else:
                        log.log(8,'audit',_('Trying next layout.'))
                        count = count + 1
                else:
                    if tmpLayout.canRun():
                        log.updateNowPlaying(str(tmpLayout.layoutID))
                        log.log(8,'audit',_('Releasing scheduler layout lock.'))
                        self.__lock.release()
                        return tmpLayout
                    else:
                        log.log(8,'audit',_('Trying next layout.'))
                        count = count + 1
        
        log.log(8,'info',_('Tried all layouts and none could run.'))
        try:
            if self.__defaultLayout.canRun():
                log.updateNowPlaying(str(self.__defaultLayout.layoutID) + " (Default)")
                log.log(8,'audit',_('Releasing scheduler layout lock.'))
                self.__lock.release()
                return self.__defaultLayout
            else:
                log.updateNowPlaying("Splash Screen")
                log.log(8,'audit',_('Releasing scheduler layout lock.'))
                self.__lock.release()
                return XiboLayout('0',False)
        except:
            log.log(8,'info',_('Exception thrown checking default layout. Falling back to Splash Screen.'))
            log.updateNowPlaying("Splash Screen")
            log.log(8,'audit',_('Releasing scheduler layout lock.'))
            self.__lock.release()
            return XiboLayout('0',False)

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
        self.liftStack = Queue.LifoQueue()
        
        try:
            self.defaultTag = config.get('LiftTags','default')
        except ConfigParser.NoOptionError:
            self.defaultTag = "default"
            log.log(0,"error",_("No LiftTags.default specified in your configuration. Defaulting to 'default'."))
        
        for i in range(0,16):
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

        try:
            self.serialPort2 = config.get('Lift','serial2')
        except:
            self.serialPort2 = '/dev/ttyUSB2'

        try:
            self.serialPort3 = config.get('Lift','serial3')
        except:
            self.serialPort3 = '/dev/ttyUSB3'
        
    def run(self):
        import serial
        
        state = [False,False,False,False,False,False,False,False,False,False,False,False,False,False,False,False]
        stats = ["","","","","","","","","","","","","","","",""]
        liftHistory = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

        ser0 = None
        ser1 = None
        ser2 = None
        ser3 = None
        
        trigger = None
        try:
            trigger = int(config.get('Lift','trigger'))
        except:
            trigger = 3
        
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

        try:
            ser2 = serial.Serial(self.serialPort2)
        except serial.SerialException:
            log.log(0,"error","Unable to open configured serial port. Switch interface disabled: " + self.serialPort2)
            log.lights('Lift9','red')
            log.lights('Lift10','red')
            log.lights('Lift11','red')
            log.lights('Lift12','red')
            ser2 = False

        try:
            ser3 = serial.Serial(self.serialPort3)
        except serial.SerialException:
            log.log(0,"error","Unable to open configured serial port. Switch interface disabled: " + self.serialPort3)
            log.lights('Lift13','red')
            log.lights('Lift14','red')
            log.lights('Lift15','red')
            log.lights('Lift16','red')
            ser3 = False


        if ser0 == False and ser1 == False and ser2 == False and ser3 == False:
            # No lifts are active. Quit now.
            return
        
        # Figure out which numbers to loop over
        loopCounter = []

        if ser0:
            loopCounter.append(0)
            
        if ser1:
            loopCounter.append(4)

        if ser2:
            loopCounter.append(8)

        if ser3:
            loopCounter.append(12)
        
        while True:
            flag = False
            offFlag = False
            activeLift = None
            
            for i in loopCounter:
                if i == 0:
                    ser = ser0
                elif i == 4:
                    ser = ser1
                elif i == 8:
                    ser = ser2
                elif i == 12:
                    ser = ser3
                    
                if ser.getCD() == state[i]:
                    if not state[i]:
                        if liftHistory[i] < trigger:
                            liftHistory[i] += 1
                        if liftHistory[i] == trigger:
                            activeLift = i
                            log.lights('Lift' + str(i + 1),'green')
                            flag = True
                            state[i] = True
                            stats[i] = str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
                    else:
                        if liftHistory[i] > 0:
                            liftHistory[i] -= 1
                        if liftHistory[i] == 0:
                            log.lights('Lift' + str(i + 1),'grey')
                            state[i] = False
                            log.stat('event', stats[i], str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())), self.tags[i], "", "", "")
                            offFlag = True                            
                if ser.getDSR() == state[1 + i]:
                    if not state[1 + i]:
                        if liftHistory[1 + i] < trigger:
                            liftHistory[1 + i] += 1
                        if liftHistory[1 + i] == trigger:
                            activeLift = i + 1
                            log.lights('Lift' + str(i + 2),'green')
                            flag = True
                            state[1 + i] = True
                            stats[1 + i] = str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
                    else:
                        if liftHistory[1 + i] > 0:
                            liftHistory[1 + i] -= 1
                        if liftHistory[1 + i] == 0:
                            log.lights('Lift' + str(i + 2),'grey')
                            state[1 + i] = False
                            log.stat('event', stats[1 + i], str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())), self.tags[i+1], "", "", "")
                            offFlag = True
                if ser.getCTS() == state[2 + i]:
                    if not state[2 + i]:
                        if liftHistory[2 + i] < trigger:
                            liftHistory[2 + i] += 1
                        if liftHistory[2 + i] == trigger:
                            activeLift = i + 2
                            flag = True
                            log.lights('Lift' + str(i + 3),'green')
                            state[2 + i] = True
                            stats[2 + i] = str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
                    else:
                        if liftHistory[2 + i] > 0:
                            liftHistory[2 + i] -= 1
                        if liftHistory[2 + i] == 0:
                            log.lights('Lift' + str(i + 3),'grey')
                            state[2 + i] = False
                            log.stat('event', stats[2 + i], str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())), self.tags[i+2], "", "", "")
                            offFlag = True
                if ser.getRI() == state[3 + i]:
                    if not state[3 + i]:
                        if liftHistory[3 + i] < trigger:
                            liftHistory[3 + i] += 1
                        if liftHistory[3 + i] == trigger:
                            activeLift = i + 3
                            flag = True
                            log.lights('Lift' + str(i + 4),'green')
                            state[3 + i] = True
                            stats[3 + i] = str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
                    else:
                        if liftHistory[3 + i] > 0:
                            liftHistory[3 + i] -= 1
                        if liftHistory[3 + i] == 0:                        
                            log.lights('Lift' + str(i + 4),'grey')
                            state[3 + i] = False
                            log.stat('event', stats[3 + i], str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())), self.tags[i+3], "", "", "")
                            offFlag = True
            
            if flag:
                log.updateLift(self.tags[activeLift])
                self.scheduler.validTag = self.tags[activeLift]
                self.liftStack.put(activeLift)
                self.displayManager.currentLM.dispose()
            
            if offFlag:
                # Work our way back down the stack of lift events until we reach a matching state
                if not (state[0] or state[1] or state[2] or state[3] or state[4] or state[5] or state[6] or state[7]
                        or state[8] or state[9] or state[10] or state[11] or state[12] or state[13] or state[14] or state[15]):
                    # All the lifts are off. Reset the liftStack and show the default
                    self.liftStack = Queue.LifoQueue()
                    self.scheduler.validTag = self.defaultTag
                    log.updateLift(self.scheduler.validTag)
                    self.displayManager.currentLM.dispose()
                else:
                    # At least one lift is still up. 
                    try:
                        inFlag = True
                        while inFlag:
                            lastLift = self.liftStack.get(False)
                            if state[lastLift] == True:
                                # The lift is still active
                                # Replace the item on the stack
                                self.liftStack.put(lastLift)
                                inFlag = False
                                if not self.scheduler.validTag == self.tags[lastLift]:
                                    self.scheduler.validTag = self.tags[lastLift]
                                    log.updateLift(self.scheduler.validTag)
                                    self.displayManager.currentLM.dispose()

                    except Queue.Empty:
                        # This shouldn't ever happen, but hey ho.
                        pass
                    
            time.sleep(0.25)
            
    
#### End Switch Input Watcher ####

#### Ticket Counter ####
class TicketCounter(Thread):
    
    def __init__(self, player):
        Thread.__init__(self)
        self.__lock = Semaphore()
        self.__lock.acquire()
        self.p = player
        self.p.counterValue = 0
        self.max = int(config.get('TicketCounter', 'maxCount'))
        self.osdBackColour = config.get('TicketCounter', 'osdBackColour')
        self.osdBackOpacity = float(config.get('TicketCounter', 'osdBackOpacity'))
        self.osdFontSize = config.get('TicketCounter', 'osdFontSize')
        self.osdFontColour = config.get('TicketCounter', 'osdFontColour')
        self.osdTimeOut = int(config.get('TicketCounter', 'osdTimeOut'))
        self.__triggers = 0
        
        useRotation = bool(not int(config.get('Main', 'vwidth')) == 0)

        if useRotation:
            self.ticketW = (int(config.get('TicketCounter', 'osdWidthPercent')) / 100.0) * int(config.get('Main', 'vwidth'))
        else:
            self.ticketW = (int(config.get('TicketCounter', 'osdWidthPercent')) / 100.0) * int(config.get('Main', 'width'))

        self.running = True

        # Draw the OSD
        tmpXML = '<rect fillcolor="%s" strokewidth="0" id="ticketCounterBG" fillopacity="%s" size="(%s,%s)" />' % (self.osdBackColour,self.osdBackOpacity,self.ticketW,self.ticketW)
        self.p.enqueue('add', (tmpXML, 'ticketCounter'))
        
    def run(self):
        # Loop forever. Block waiting for the lock to be released
        # by an increment, reset or lock event.
        while self.running:
            self.__lock.acquire()
            if self.running:
                self.update()

    def update(self):

        # Update OSD number and display
        if self.p.ticketOSD:
            tmpXML = '<words id="ticketCounterText" alignment="center" width="%s" pos="(%s,10)" opacity="1" text="%s" font="Arial" color="%s" fontsize="%s" />' % (self.ticketW,(self.ticketW/2),self.p.counterValue,self.osdFontColour,self.osdFontSize)
            self.p.enqueue('del', 'ticketCounterText')
            self.p.enqueue('add', (tmpXML, 'ticketCounter'))
            self.p.enqueue('setOpacity', ('ticketCounter', 1))
            self.p.enqueue('timer', (self.osdTimeOut, self.fadeOutOSD))
            self.__triggers = self.__triggers + 1

        # Update any TicketCounter region
        self.p.enqueue('updateCounter', self.p.counterValue)
        

    def fadeOutOSD(self):
        self.__triggers = self.__triggers - 1

        if self.__triggers == 0:
            self.p.enqueue('anim', ('fadeOut', 'ticketCounter', 250, None))

    def increment(self):
        # Incremement the counter by one, or reset to 1 if hit max
        if self.p.counterValue == self.max:
            self.p.counterValue = 1
        else:
            self.p.counterValue = self.p.counterValue + 1

        self.__lock.release()
        log.log(1,"info",_("TicketCounter: Next Customer Please %s") % self.p.counterValue,True)

    def decrement(self):
        # Decremement the counter by one, or reset to max if hit 1 or is reset to 0
        if self.p.counterValue < 2:
            self.p.counterValue = self.max
        else:
            self.p.counterValue = self.p.counterValue - 1

        self.__lock.release()
        log.log(1,"info",_("TicketCounter: Next Customer Please %s") % self.p.counterValue,True)

    def reset(self):
        self.p.counterValue = 0
        self.__lock.release()
        log.log(1,"info",_("TicketCounter: Reset"),True)

    def quit(self):
        self.running = False
        self.__lock.release()

    
#### End Ticket Counter ####

#### Webservice
class XMDSException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class XMDS:
    def __init__(self):
        self.__schemaVersion__ = "3"

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

        licenseKey = ''
        try:
            licenseKey = config.get('Main','xmdsLicenseKey')
        except:
            pass

        if licenseKey != '':
            self.uuid = licenseKey

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
        
        self.socketTimeout = None
        try:
            self.socketTimeout = int(config.get('Main','socketTimeout'))
        except:
            self.socketTimeout = 30
        
        try:
            socket.setdefaulttimeout(self.socketTimeout)
            log.log(2,"info",_("Set socket timeout to: ") + str(self.socketTimeout))
        except:
            log.log(0,"warning",_("Unable to set socket timeout. Using system default"))
            
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

        # Work out the URL for XMDS and add HTTP URL quoting (ie %xx)
        self.wsdlFile = self.xmdsUrl + '?wsdl'
        
        # Work out the host that XMDS is on so we can get an IP address for ourselves
        tmpParse = urlparse.urlparse(self.xmdsUrl)
        self.xmdsHost = tmpParse.hostname
        del tmpParse
        
    def getIP(self):
        tmpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        tmpSocket.connect((self.xmdsHost,0))
        return str(tmpSocket.getsockname()[0])
    
    def getDisk(self):
        s = os.statvfs(config.get('Main','libraryDir'))
        return (s.f_bsize * s.f_blocks,s.f_bsize * s.f_bavail)

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
                    log.log(2,"info",_("Connected to XMDS via WSDL at %s") % self.wsdlFile)
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
                # Update the IP Address shown on the infoScreen
                log.updateIP(self.getIP())
            except:
                pass
            log.updateFreeSpace(self.getDisk())
            try:
                req = self.server.RequiredFiles(self.getKey(),self.getUUID(),self.__schemaVersion__)
            except SOAPpy.Types.faultType, err:
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
            except AttributeError, err:
                log.lights('RF','red')
                log.log(0,"error",str(err))
                self.hasInitialised = False
                raise XMDSException("RequiredFiles: webservice not initialised")
            except KeyError, err:
                log.lights('RF', 'red')
                log.log(0,"error",str(err))
                self.hasInitialised = False
                raise XMDSException("RequiredFiles: Webservice returned non XML content")
        else:
            log.log(0,"error","XMDS could not be initialised")
            log.lights('RF','grey')
            raise XMDSException("XMDS could not be initialised")

        log.lights('RF','green')
        return req

    def GetResource(self,layoutID,regionID,mediaID):
        """Connect to XMDS and get a resource"""

        req = None
        if self.check():
            try:
                req = self.server.GetResource(self.getKey(),self.getUUID(), int(layoutID), regionID, mediaID, self.__schemaVersion__)
            except SOAPpy.Types.faultType, err:
                raise XMDSException("GetResource: Incorrect arguments passed to XMDS.")
            except SOAPpy.Errors.HTTPError, err:
                log.log(0,"error",str(err))
                raise XMDSException("GetResource: HTTP error connecting to XMDS.")
            except socket.error, err:
                log.log(0,"error",str(err))
                raise XMDSException("GetResource: socket error connecting to XMDS.")
            except AttributeError, err:
                log.log(0,"error",str(err))
                self.hasInitialised = False
                raise XMDSException("GetResource: webservice not initialised")
            except KeyError, err:
                log.log(0,"error",str(err))
                self.hasInitialised = False
                raise XMDSException("GetResource: Webservice returned non XML content")
        else:
            log.log(0,"error","XMDS could not be initialised")
            raise XMDSException("XMDS could not be initialised")

        return req
    
    def SubmitLog(self,logXml):
        response = None
        log.lights('Log','amber')
        
        if self.check():
            try:
                # response = self.server.SubmitLog(serverKey=self.getKey(),hardwareKey=self.getUUID(),logXml=logXml,version="1")
                response = self.server.SubmitLog(self.__schemaVersion__,self.getKey(),self.getUUID(),logXml)
            except SOAPpy.Types.faultType, err:
                print(str(err))
                log.log(0,"error",str(err))
                log.lights('Log','red')
                raise XMDSException("SubmitLog: Incorrect arguments passed to XMDS.")
            except SOAPpy.Errors.HTTPError, err:
                print(str(err))
                log.log(0,"error",str(err))
                log.lights('Log','red')
                raise XMDSException("SubmitLog: HTTP error connecting to XMDS.")
            except socket.error, err:
                print(str(err))
                log.log(0,"error",str(err))
                log.lights('Log','red')
                raise XMDSException("SubmitLog: socket error connecting to XMDS.")
            except KeyError, err:
                print("KeyError: " + str(err))
                log.log(0,"error","KeyError: " + str(err))
                log.lights('Log','red')
                raise XMDSException("SubmitLog: Key error connecting to XMDS.")
            except AttributeError, err:
                log.lights('Log','red')
                log.log(0,"error",str(err))
                self.hasInitialised = False
                raise XMDSException("SubmitLog: webservice not initialised")
            except KeyError, err:
                log.lights('Log', 'red')
                log.log(0,"error",str(err))
                self.hasInitialised = False
                raise XMDSException("SubmitLog: Webservice returned non XML content")
            except:
                print("SubmitLog: An unexpected error occured.")
                log.lights('Log','red')
                raise XMDSException("SubmitLog: Unknown exception was handled.")
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
                response = self.server.SubmitStats(self.__schemaVersion__,self.getKey(),self.getUUID(),statXml)
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
            except KeyError, err:
                log.log(0,"error","KeyError: " + str(err))
                log.lights('Stat','red')
                raise XMDSException("SubmitStats: Key error connecting to XMDS.")
            except AttributeError, err:
                log.lights('Stat','red')
                log.log(0,"error",str(err))
                self.hasInitialised = False
                raise XMDSException("SubmitStats: webservice not initialised")
            except KeyError, err:
                log.lights('Stat', 'red')
                log.log(0,"error",str(err))
                self.hasInitialised = False
                raise XMDSException("SubmitStats: Webservice returned non XML content")
            except:
                print("SubmitStats: An unexpected error occured.")
                log.lights('Stat','red')
                raise XMDSException("SubmitStats: Unknown exception was handled.")
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
                try:
                    req = self.server.Schedule(self.getKey(),self.getUUID(),self.__schemaVersion__)
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
                except AttributeError, err:
                    log.lights('S','red')
                    log.log(0,"error",str(err))
                    self.hasInitialised = False
                    raise XMDSException("Schedule: webservice not initialised")
                except KeyError, err:
                    log.lights('S', 'red')
                    log.log(0,"error",str(err))
                    self.hasInitialised = False
                    raise XMDSException("Schedule: Webservice returned non XML content")
            except AttributeError, err:
                # For some reason the except SOAPpy.Types line above occasionally throws an
                # exception when the client first starts saying SOAPpy doesn't have a Types attribute
                # Catch that here I guess!
                log.lights('S','red')
                log.log(0,"error",str(err))
                self.hasInitiated = False
                raise XMDSException("RequiredFiles: webservice not initalised")
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
                response = self.server.GetFile(self.getKey(),self.getUUID(),tmpPath,tmpType,tmpOffset,tmpChunk,self.__schemaVersion__)
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
            except AttributeError, err:
                log.lights('GF','red')
                log.log(0,"error",str(err))
                self.hasInitialised = False
                raise XMDSException("GetFile: webservice not initialised")
            except KeyError, err:
                log.lights('GF', 'red')
                log.log(0,"error",str(err))
                self.hasInitialised = False
                raise XMDSException("GetFile: Webservice returned non XML content")
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
                    try:
                        regReturn = self.server.RegisterDisplay(self.getKey(),self.getUUID(),self.getName(),self.__schemaVersion__)
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
                    except AttributeError, err:
                        log.lights('RD','red')
                        log.log(0,"error",str(err))
                        self.hasInitialised = False
                    except KeyError, err:
                        log.lights('RD', 'red')
                        log.log(0,"error",str(err))
                        self.hasInitialised = False

                if regReturn != regOK:
                    # We're not licensed. Sleep 20 * tries seconds and try again.
                    log.log(0,"info",_("Waiting for license to be issued, or connection restored to the webservice. Set requireXMDS=false to skip this check"))
                    log.lights('RD','red')
                    time.sleep(regInterval * tries)
            # End While
            log.lights('RD','green')
        else:
            if self.check():
                try:
                    log.log(0,"info",self.server.RegisterDisplay(self.getKey(),self.getUUID(),self.getName(),self.__schemaVersion__))
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
                except AttributeError, err:
                    log.lights('RD','red')
                    log.log(0,"error",str(err))
                    self.hasInitialised = False
                except KeyError, err:
                    log.lights('RD', 'red')
                    log.log(0,"error",str(err))
                    self.hasInitialised = False

    def MediaInventory(self,inventoryXml):
        response = None
        log.lights('Log','amber')
        
        if self.check():
            try:
                response = self.server.MediaInventory(self.__schemaVersion__,self.getKey(),self.getUUID(),inventoryXml)
            except SOAPpy.Types.faultType, err:
                print(str(err))
                log.log(0,"error",str(err))
                log.lights('Log','red')
                raise XMDSException("MediaInventory: Incorrect arguments passed to XMDS.")
            except SOAPpy.Errors.HTTPError, err:
                print(str(err))
                log.log(0,"error",str(err))
                log.lights('Log','red')
                raise XMDSException("MediaInventory: HTTP error connecting to XMDS.")
            except socket.error, err:
                print(str(err))
                log.log(0,"error",str(err))
                log.lights('Log','red')
                raise XMDSException("MediaInventory: socket error connecting to XMDS.")
            except KeyError, err:
                print("KeyError: " + str(err))
                log.log(0,"error","KeyError: " + str(err))
                log.lights('Log','red')
                raise XMDSException("MediaInventory: Key error connecting to XMDS.")
            except AttributeError, err:
                log.lights('Log','red')
                log.log(0,"error",str(err))
                self.hasInitialised = False
                raise XMDSException("MediaInventory: webservice not initialised")
            except KeyError, err:
                log.lights('Log', 'red')
                log.log(0,"error",str(err))
                self.hasInitialised = False
                raise XMDSException("MediaInventory: Webservice returned non XML content")
            except:
                print("MediaInventory: An unexpected error occured.")
                log.lights('Log','red')
                raise XMDSException("MediaInventory: Unknown exception was handled.")
        else:
            log.log(0,"error","XMDS could not be initialised")
            log.lights('Log','grey')
            raise XMDSException("XMDS could not be initialised")
        
        log.lights('Log','green')
        return response

class XMDSOffline(Thread):
    def __init__(self,displayManager):
        Thread.__init__(self)
        self.__schemaVersion__ = "2"
        self.displayManager = displayManager
        self.updatePath = ""
        self.__running__ = True
        self.__scanPath__ = '/media'

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

        licenseKey = ''
        try:
            licenseKey = config.get('Main','xmdsLicenseKey')
        except:
            pass

        if licenseKey != '':
            self.uuid = licenseKey

        self.name = None
        try:
            self.name = config.get('Main','xmdsClientName')
        except:
            pass

        if self.name == None or self.name == "":
            import platform
            self.name = platform.node()

        self.start()

    def run(self):
        # Sleep for 10 seconds to allow the client time to start and settle.
        time.sleep(10)

        # Startup a loop listening scanning for new mounts
        log.log(5,'info','Offline Update: Scanning.',True)
        while self.__running__:
            for folder in os.listdir(self.__scanPath__):
                log.log(5,'info','Offline Update: Checking %s for new content.' % os.path.join(self.__scanPath__,folder),True)
                log.log(5,'info','Offline Update: Client License Key: %s' % self.uuid,True)
                if os.path.isdir(os.path.join(self.__scanPath__,folder,self.uuid)):
                    log.log(5,'info','Offline Update: Starting update from %s.' % os.path.join(self.__scanPath__,folder,self.uuid),True)
                    self.updatePath = os.path.join(self.__scanPath__,folder)
                    self.displayManager.scheduler.collect()
                    time.sleep(5)
                    self.displayManager.downloader.collect()
            log.log(5,'info','Offline Update: Sleeping 30 seconds.',True)
            time.sleep(30)
       
    def getIP(self):
        return 'Offline Mode'
    
    def getDisk(self):
        s = os.statvfs(config.get('Main','libraryDir'))
        return (s.f_bsize * s.f_blocks,s.f_bsize * s.f_bavail)

    def getUUID(self):
        return str(self.uuid)

    def getName(self):
        return str(self.name)

    def getKey(self):
        return 'Offline'

    def check(self):
        return True

    def RequiredFiles(self):
        """Connect to XMDS and get a list of required files"""
        log.lights('RF','amber')
        req = None
        if self.check():
            try:
                # Update the IP Address shown on the infoScreen
                log.updateIP(self.getIP())
            except:
                pass

            log.updateFreeSpace(self.getDisk())
            
            try:
                fh = open(os.path.join(self.updatePath,self.uuid,'rf.xml'), 'r')
                req = fh.read()
                fh.close()
            except IOError:
                log.lights('RF','red')
                raise XMDSException("XMDS could not be initialised")

        else:
            log.log(0,"error","XMDS could not be initialised")
            log.lights('RF','grey')
            raise XMDSException("XMDS could not be initialised")

        log.lights('RF','green')
        return req
    
    def SubmitLog(self,logXml):
        pass
    
    def SubmitStats(self,statXml):
        pass

    def Schedule(self):
        """Connect to XMDS and get the current schedule"""
        log.lights('S','amber')
        req = None
        if self.check():
            try:
                fh = open(os.path.join(self.updatePath,self.uuid,'schedule.xml'), 'r')
                req = fh.read()
                fh.close()
            except IOError:
                log.lights('S','red')
                raise XMDSException("XMDS could not be initialised")
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
            if tmpType == 'media':
                try:
                    fh = open(os.path.join(self.updatePath,self.uuid,tmpPath), 'r')
                    fh.seek(tmpOffset)
                    response = fh.read(tmpChunk)
                    fh.close()
                except:
                    log.lights('GF','red')
                    raise XMDSException("XMDS could not be initialised")
            if tmpType == 'layout':
                try:
                    fh = open(os.path.join(self.updatePath,self.uuid,tmpPath), 'r')
                    response = fh.read()
                    fh.close()
                except:
                    log.lights('GF','red')
                    raise XMDSException("XMDS could not be initialised")
            if tmpType == 'blacklist':
                response = ""
        else:
            log.log(0,"error","XMDS could not be initialised")
            log.lights('GF','grey')
            raise XMDSException("XMDS could not be initialised")

        log.lights('GF','green')
        return response

    def RegisterDisplay(self):
        log.lights('RD','amber')
        time.sleep(5)
        log.lights('RD','green')

#### Finish Webservice

class XiboDisplayManager:
    def __init__(self):
        pass

    def run(self):
        # Run up a XiboLogScreen temporarily until XMDS is initialised.
        global log
        logLevel = config.get('Logging','logLevel')
        log = XiboLogScreen(logLevel)
        
        if config.get('Main','manualUpdate') == 'true':
            self.xmds = XMDSOffline(self)
        else:
            self.xmds = XMDS()
        
        # Check data directory exists
        try:
            libDir = config.get('Main','libraryDir')
            if not os.path.isdir(os.path.join(libDir,'scaled')):
                os.makedirs(os.path.join(libDir,'scaled'))
        except os.error:
            log.log(0,"error",_("Unable to create local library directory %s") % libDir)
            exit(1)
        except ConfigParser.NoOptionError:
            log.log(0,"error",_("No libraryDir specified in your configuration"))
            exit(1)            
                
        print _("Log Level is: ") + logLevel
        print _("Logging will be handled by: ") + config.get('Logging','logWriter')
        print _("Switching to new logger")

        logWriter = config.get('Logging','logWriter')
        log = eval(logWriter)(logLevel)

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
        self.currentLM = XiboLayoutManager(self, self.Player, XiboLayout('0',False), 0, 1.0, True)
        self.currentLM.start()

        # Let the log object see the player so it can update the hidden info screen
        # and XMDS so it can send data to the webservice if it needs to.
        log.setupInfo(self.Player)
        log.setXmds(self.xmds)
        
        # Load a DownloadManager and start it running in its own thread
        try:
            downloaderName = config.get('Main','downloader')
            self.downloader = eval(downloaderName)(self.xmds,self.Player)
            self.downloader.start()
            log.log(2,"info",_("Loaded Download Manager ") + downloaderName)
        except ConfigParser.NoOptionError:
            log.log(0,"error","NoOptionError")
            log.log(0,"error",_("No DownloadManager specified in your configuration."))
            log.log(0,"error",_("Please check your Download Manager configuration."))
            exit(1)
        except:
            log.log(0,"error","Unexpected Exception")
            log.log(0,"error",downloaderName + _(" does not implement the methods required to be a Xibo DownloadManager or does not exist."))
            log.log(0,"error",_("Please check your Download Manager configuration."))
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
        
        try:
            self.liftEnabled = config.get('Lift','enabled')
            if self.liftEnabled == "false":
                self.liftEnabled = False
                log.log(3,"audit",_("Disabling lift functionality in Logger"))
            else:
                self.liftEnabled = True
                log.log(3,"audit",_("Enabling lift functionality in Logger"))
        except:
            self.liftEnabled = False
            log.log(3,"error",_("Lift->enabled not defined in configuration. Disabling lift functionality in Logger"))

        
        # Thread to watch the switch inputs and control the scheduler
        if self.liftEnabled:
            self.switch = SwitchWatcher(self.scheduler,self)
            self.switch.start()

        # Thread to watch Ticket Counter value and update the display as required
        self.ticketCounter = TicketCounter(self.Player)
        self.ticketCounter.start()

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
        self.Player.ticketOSD = True
        self.currentLM = XiboLayoutManager(self, self.Player, self.scheduler.nextLayout())
        log.log(2,"info",_("XiboLayoutManager: nextLayout() -> Starting new XiboLayoutManager with layout ") + str(self.currentLM.l.layoutID))
        self.currentLM.start()
        self.Player.enqueue('del',tmpLayout)

class XiboPlayer(Thread):
    "Class to handle libavg interactions"
    def __init__(self,parent):
        self.__lock = Semaphore()

        # Acquire the lock so that nothing can enqueue stuff until this thread
        # starts
        self.__lock.acquire()

        Thread.__init__(self)
        self.info = False
        self.osLog = False
        self.osLogX = 0
        self.osLogY = 0
        self.q = Queue.Queue(0)
        self.uniqueId = 0
        self.dim = (int(config.get('Main', 'width')),
                    int(config.get('Main', 'height')))
        self.currentFH = None
        self.parent = parent

        self.ticketOSD = True

        self.ticketCounterNextScanCode = int(config.get('TicketCounter', 'nextScanCode'))
        self.ticketCounterResetScanCode = int(config.get('TicketCounter', 'resetScanCode'))
        self.ticketCounterPrevScanCode = int(config.get('TicketCounter', 'prevScanCode'))
        self.counterValue = 0
        self.counterID = 0

    def enableTicketOSD(self):
        self.ticketOSD = True

    def disableTicketOSD(self):
        self.ticketOSD = False

    def getDimensions(self):
        # NB: I don't think this is ever used.
        return self.dim

    def getElementByID(self,id):
        return self.player.getElementByID(id)

    def nextCounterId(self):
        self.counterID += 1

        if self.counterID > 10:
            self.counterID = 1

        return self.counterID

    def nextUniqueId(self):
        # This is just to ensure there are never two identically named nodes on the
        # player at once.
        # When we hit 100 times, reset to 0 as those nodes should be long gone.
        if self.uniqueId > 100:
            self.uniqueId = 0

        self.uniqueId += 1
        return self.uniqueId

    def run(self):
        log.log(1, 'info', _("New XiboPlayer running"))
        self.player = avg.Player.get()
        
        if config.get('Main', 'fullscreen') == "true":
            self.player.setResolution(
                True,
                int(config.get('Main', 'width')),
                int(config.get('Main', 'height')),
                int(config.get('Main', 'bpp'))
            )
        else:
            self.player.setResolution(
                False,
                int(config.get('Main', 'width')),
                int(config.get('Main', 'height')),
                int(config.get('Main', 'bpp'))
            )

        try:
            if int(config.get('Main', 'fps')) > 0:
                fps = int(config.get('Main', 'fps'))
                self.player.setFramerate(fps)
        except ValueError:
            log.log(0, 'error', _('Your configuration for fps is incorrect.'
                                  ' Main->FPS should be an integer value.'))
            log.log(0, 'error', _('Using 60fps as a default.'))            
            fps = 60
            self.player.setFramerate(fps)
        except ConfigParser.NoOptionError:
            pass
        
        # Check Counter for duplicate scan codes
        nS = int(config.get('TicketCounter', 'nextScanCode'))
        pS = int(config.get('TicketCounter', 'prevScanCode'))
        rS = int(config.get('TicketCounter', 'resetScanCode'))

        if (nS == pS):
            log.log(0, 'warn', _('nextScanCode is identical to prevScanCode in your configuration. You almost certainly don\'t want that'))

        if (nS == rS):
            log.log(0, 'warn', _('nextScanCode is identical to resetScanCode in your configuration. You almost certainly don\'t want that'))

        if (rS == pS):
            log.log(0, 'warn', _('resetScanCode is identical to prevScanCode in your configuration. You almost certainly don\'t want that'))


        # Load the BrowserNode plugin
        self.player.loadPlugin("libbrowsernode")
        
        self.player.showCursor(0)
        self.player.volume = 1
        self.player.stopOnEscape(False)
        
        useRotation = bool(not int(config.get('Main', 'vwidth')) == 0)
        
        # Calculate the information window
        if useRotation:
            infoX = (int(config.get('Main', 'vwidth')) - 400) / 2
            infoY = (int(config.get('Main', 'vheight')) - 300) / 2
            self.osLogX = int(config.get('Main', 'vwidth'))
            self.osLogY = int(config.get('Main', 'vheight')) - 20
        else:
            infoX = (int(config.get('Main', 'width')) - 400) / 2
            infoY = (int(config.get('Main', 'height')) - 300) / 2
            self.osLogX = int(config.get('Main', 'width'))
            self.osLogY = int(config.get('Main', 'height')) - 20
        
        # If the info window is bigger than the client, stick it in the top
        # left corner.
        if infoX < 0:
            infoX = 0
        if infoY < 0:
            infoY = 0

        # Calculate the TicketCounter div
        if useRotation:
            ticketW = (int(config.get('TicketCounter', 'osdWidthPercent')) / 100.0) * int(config.get('Main', 'vwidth'))
            ticketX = (int(config.get('Main', 'vwidth')) - ticketW) / 2
            ticketY = (int(config.get('Main', 'vheight')) - ticketW) / 2
        else:
            ticketW = (int(config.get('TicketCounter', 'osdWidthPercent')) / 100.0) * int(config.get('Main', 'width'))
            ticketX = (int(config.get('Main', 'width')) - ticketW) / 2
            ticketY = (int(config.get('Main', 'height')) - ticketW) / 2

        if ticketX < 0:
            ticketX = 0
        if ticketY < 0:
            ticketY = 0

        if useRotation:
            # The layout rotates around the centre so figure out how far we need to move it up/down or left/right to get it centred
            # before it's rotated.
            oX = (int(config.get('Main','width')) / 2.0) - (int(config.get('Main','vwidth')) / 2.0)
            oY = (int(config.get('Main','height')) / 2.0) - (int(config.get('Main','vheight')) / 2.0)
            
            # Convert degrees in the config to Radians
            oR = math.radians(float(config.get('Main','vrotation')))
        
        # Build the XML that defines the avg node and divs for screen and information
        avgContent = '<avg id="main" width="%s" height="%s">' % (config.get('Main','width'), config.get('Main','height'))
        if useRotation:
            avgContent += '<div pos="(%s,%s)" id="rotation" width="%s" height="%s" angle="%s" crop="False">' % (oX,oY,config.get('Main','vwidth'), config.get('Main','vheight'), oR)
        avgContent += '<div id="screen" pos="(0,0)" crop="False" />'
        avgContent += '<div id="ticketCounter" width="%d" height="%d" x="%d" y="%d" opacity="0" crop="False" />' % (ticketW,ticketW,ticketX,ticketY)
        avgContent += '<div id="osLog" pos="(0,%d)" width="%d" height="20" opacity="0" />' % (self.osLogY,self.osLogX)
        avgContent += '<div id="info" width="400" height="300" x="%d" y="%d" opacity="0" crop="False" />' % (infoX,infoY)
        avgContent += '<div id="offlineUpdate" width="100" height="100" x="0" y="0" opacity="1" crop="False" />'
        if useRotation:
            avgContent += '</div>'
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

        if self.osLog:
            log.log(0,"info",_("Detected keypress with scancode %s") % e.scancode,True)

        if e.scancode == self.ticketCounterNextScanCode:
            try:
                self.parent.ticketCounter.increment()    
            except:
                pass

        if e.scancode == self.ticketCounterResetScanCode:
            try:
                self.parent.ticketCounter.reset()
            except:
                pass

        if e.scancode == self.ticketCounterPrevScanCode:
            try:
                self.parent.ticketCounter.decrement()
            except:
                pass


        if self.info:
            # Process key strokes that are only active when the info
            # screen is showing
            if e.keystring == "n":
                self.parent.currentLM.dispose()
            
            if e.keystring == "r":
                self.parent.downloader.collect()
                self.parent.scheduler.collect()

            if e.keystring == "l":
                if self.osLog:
                    self.osLog = False
                    self.enqueue('setOpacity',('osLog',0))
                else:
                    self.osLog = True
                    self.enqueue('setOpacity',('osLog',1))
            
            if e.keystring == "q":
                #TODO: Fully implement a proper quit function
                # Allow threads a chance to stop nicely before finally killing
                # the lot off.
                log.flush()

                try:
                    self.parent.downloader.running = False
                    self.parent.downloader.collect()
                except:
                    pass
                
                try:
                    self.parent.scheduler.running = False
                    self.parent.scheduler.collect()
                except:
                    pass

                try:
                    self.parent.ticketCounter.quit()
                except:
                    pass

                log.log(5,"info",_("Blocking waiting for Scheduler"))
                try:
                    self.parent.scheduler.join()
                except:
                    pass

                log.log(5,"info",_("Blocking waiting for DownloadManager"))
                try:
                    self.parent.downloader.join()
                except:
                    pass
                
                log.log(5,"info",_("Blocking waiting for Player"))
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
                        animation = avg.fadeIn(currentNode,data[2],1,data[3])
                    if data[0] == "fadeOut":
                        animation = avg.fadeOut(currentNode,data[2],data[3])
                    if data[0] == "linear":
                        animation = anim.LinearAnim(currentNode,data[3],data[2],data[4],data[5],False,data[6])
                    if data[0] == "ease":
                        animation = anim.EaseInOutAnim(currentNode,data[3],data[2],data[4],data[5],data[7],data[8],False,data[6],None)
                    if data[0] == "continuous":
                        animation = anim.ContinuousAnim(currentNode,data[2],data[3],data[4])
                    animation.start()
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
                    currentNode.opacity = float(data[1])
                elif cmd == "setAngle":
                    currentNode = self.player.getElementByID(data[0])
                    currentNode.angle = data[1]
                elif cmd == "browserNavigate":
                    currentNode = self.player.getElementByID(data[0])
                    if data[2] != None:
                        currentNode.onFinishLoading = data[2]
                    currentNode.loadUrl(data[1])
                elif cmd == "browserOptions":
                    currentNode = self.player.getElementByID(data[0])
                    if not data[1] == None:
                        currentNode.transparent = data[1]
                    if not data[2] == None:
                        if data[2] == False:
                            currentNode.executeJavascript("document.body.style.overflow='hidden';")
                elif cmd == "executeJavascript":
                    currentNode = self.player.getElementByID(data[0])
                    currentNode.executeJavascript(data[1])
                elif cmd == "zoomIn":
                    # BrowserNode Zoom In
                    currentNode = self.player.getElementByID(data)
                    currentNode.zoomIn()
                elif cmd == "zoomOut":
                    # BrowserNode Zoom Out
                    currentNode = self.player.getElementByID(data)
                    currentNode.zoomOut()
                elif cmd == "setBitmap":
                    currentNode = self.player.getElementByID(data[0])
                    currentNode.setBitmap(data[1])
                elif cmd == "effect":
                    currentNode = self.player.getElementByID(data[1])
                    if data[0] == "shadow":
                        effect = avg.ShadowFXNode()
                        effect.setParams(data[2],data[3],data[4],data[5])
                        currentNode.setEffect(effect)
                    elif data[0] == "blur":
                        effect = avg.BlurFXNode()
                        effect.setParam(data[2])
                        currentNode.setEffect(effect)
                elif cmd == "updateCounter":
                    # Iterate over all the BrowserNodes and
                    # Call the update method on them
                    for i in range(1,11):
                        try:
                            currentNode = self.player.getElementByID('counter%s' % i)
                            currentNode.executeJavascript("updateCounter('%s');" % self.counterValue)
                        except:
                            pass
                    
                self.q.task_done()
                # Call ourselves again to action any remaining queued items
                # This does not make an infinite loop since when all queued
                # items are processed.
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
            # Generic catchall to prevent unhandled player exceptions bringing
            # us down.
            except:
                # log.log(0,"error",_("An unspecified error occured: ") + str(sys.exc_info()[0]))
                self.__lock.release()
                log.log(0,"audit",_("An unspecified error occured: ") + str(cmd) + " : " + str(data))
        except AttributeError:
            log.log(0,"error","Caught that thing that makes the player crash on startup!")
            
            
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

