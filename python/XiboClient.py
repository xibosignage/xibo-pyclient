#!/usr/bin/python
# -*- coding: utf-8 -*-

from libavg import avg, anim
from xml.dom import minidom
import time, Queue
import os
import re
import time
import sys
from threading import Thread

class XiboDisplayManager:
    def __init__(self):
        pass
    
    def run(ClientRef):
        pass
    
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
    def __init__(self):
        pass

class DummyScheduler(Thread):
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
        self.dm = XiboDisplayManager()

    def play(self):
        self.dm.run()

# Main - create a XiboClient and run
xc = XiboClient()
xc.play()