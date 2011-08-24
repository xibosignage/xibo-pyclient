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

from XiboMedia import XiboMedia
from threading import Thread
import urllib
import math

class WebpageMedia(XiboMedia):
    def add(self):
        zoomLevel = self.calculateZoomLevel()
        tmpXML = '<browser id="' + self.mediaNodeName + '" opacity="0" width="' + str(self.width) + '" height="' + str(self.height) + \
                '" zoomLevel="' + str(zoomLevel) + '"/>'
        self.p.enqueue('add',(tmpXML,self.regionNodeName))

    def run(self):
        self.p.enqueue('browserNavigate',(self.mediaNodeName,urllib.unquote(str(self.options['uri'])),self.finishedRendering))
        self.p.enqueue('timer',(int(self.duration) * 1000,self.parent.next))
        self.startStats()

    def requiredFiles(self):
        return []
	
    def dispose(self):
        self.returnStats()
        self.p.enqueue('del',self.mediaNodeName)
        self.parent.tNext()

    def calculateZoomLevel(self):
        # Calling the zoomIn/zoomOut methods of a browser causes a 20% zoom in/out
        # Calculate how many calls to make
        n = 100
        count = 0
        try:
            n = int(self.options['scaling'])
        except:
            pass
        
        if n == 100:
            pass
        else:
            if n < 100:
                # Zoom Out
                count = -int(math.ceil((100 - n) / 20.0))
            else:
                # Zoom In
                count = int(math.ceil((n - 100) / 20.0))
        return count
    
    def finishedRendering(self):
        bo = self.browserOptions()
        optionsTuple = (self.mediaNodeName,bo[0],bo[1])
        self.p.enqueue('browserOptions',optionsTuple)
                
        # Make the browser visible
        self.p.enqueue('setOpacity',(self.mediaNodeName,1))
    
    def browserOptions(self):
        scroll = False
        trans = False
        
        # Decide if the browser background should be transparent
        try:
            if self.options['transparency'] == "1":
                trans = True
        except:
            pass
        
        return (trans,scroll)
