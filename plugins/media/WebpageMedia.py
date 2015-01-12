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
import os
import sys
import codecs

class WebpageMedia(XiboMedia):
    def add(self):
        self.tmpPath = os.path.join(self.libraryDir,self.mediaNodeName + "-zoom-tmp.html")
        self.retryCount = 0
        tmpXML = '<browser id="' + self.mediaNodeName + '" opacity="0" width="' + str(self.width) + '" height="' + str(self.height) + '"/>'
        self.p.enqueue('add',(tmpXML,self.regionNodeName))

    def run(self):
        self.zoomOffsetWrapper()
        self.p.enqueue('browserNavigate',(self.mediaNodeName,self.options['uri'],self.finishedRendering))
        self.startStats()

    def requiredFiles(self):
        return []
	
    def dispose(self):
        self.returnStats()
        self.p.enqueue('del',self.mediaNodeName)

        try:
            os.remove(self.tmpPath)
        except:
            pass

        self.parent.tNext()

    def finishedRendering(self):
        bo = self.browserOptions()
        optionsTuple = (self.mediaNodeName,bo[0],bo[1])
        self.p.enqueue('browserOptions',optionsTuple)
        currentNode = self.p.getElementByID(self.mediaNodeName)
        if currentNode.painted():
            # Make the browser visible
            self.p.enqueue('setOpacity',(self.mediaNodeName,1))
            self.p.enqueue('timer',(int(self.duration) * 1000,self.parent.next))
        else:
            if self.retryCount > 3:
                print "Error rendering %s. Skipping" % self.mediaNodeName
                self.parent.next()
            else:
                if self.retryCount > 1:
                    print "Error rendering %s. Re-rendering" % self.mediaNodeName
   
                self.retryCount = self.retryCount + 1
                self.p.enqueue('browserNavigate',(self.mediaNodeName,self.options['uri'],self.finishedRendering))
    
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

    def zoomOffsetWrapper(self):
        # Decode the URI
        self.options['uri'] = urllib.unquote(str(self.options['uri']))

        try:
            scaling = self.options['scaling']
        except:
            scaling = "100"

        w = self.width
        h = self.height
        zoom = ""
        iframe = ""
        offsetLeft = ""
        offsetTop = ""

        if (scaling != "100"):
            scaling = int(scaling) / 100.0
            w = w * (1 / scaling)
            h = h * (1 / scaling)
            zoom = "-webkit-transform: scale(%s); -webkit-transform-origin: 0 0;" % scaling

        try:
            offsetTop = self.options['offsetTop']
        except:
            offsetTop = "0"

        try:
            offsetLeft = self.options['offsetLeft']
        except:
            offsetLeft = "0"
    
        # The layout is zoomed or moved
        # Wrap it in an iframe
        if zoom != "" or offsetTop != "0" or offsetLeft != "0":
            iframe = "<html><body style='margin:0; border:0;'><iframe style='border:0;margin-left:-%spx; margin-top:-%spx;%s' scrolling=\"no\" width=\"%spx\" height=\"%spx\" src=\"%s\"></body></html>"
            iframe = iframe % (offsetLeft, offsetTop, zoom, int(w) + int(offsetLeft), int(h) + int(offsetTop), self.options['uri'])

            # Write the iframe to a file and overwrite the uri option to point to our temporary location
            try:
                try:
                    f = codecs.open(self.tmpPath,mode='w',encoding="utf-8")
                    f.write(iframe)
                    iframe = None
                finally:
                    f.close()
            except:
                self.log.log(0,"error","Unable to write " + self.tmpPath)
                self.parent.next()
                return
            
            # Navigate the browser to the temporary file
            self.options['uri'] = "file://" + os.path.abspath(self.tmpPath)
