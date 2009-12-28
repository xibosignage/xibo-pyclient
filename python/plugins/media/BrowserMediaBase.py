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
import sys, os

class BrowserMediaBase(XiboMedia):
        
    def add(self):
        self.tmpPath = "data" + os.sep + self.mediaNodeName + "-tmp.html"
        tmpXML = '<browser id="' + self.mediaNodeName + '" opacity="0" width="' + str(self.width) + '" height="' + str(self.height) + '"/>'
        self.p.enqueue('add',(tmpXML,self.regionNodeName))

    def run(self):
        # Open the HTML template file and read it in to a string
        try:
            try:
                f = open("resources/HtmlTemplate.htm","r")
                tmpHtml = f.read()
            finally:
                f.close()
        except IOError:
            log.log(0,"error","Unable to open %s for reading." % ("resources/HtmlTemplate.htm"))
            self.parent.next()
            return
        
        # Write the two out to temporary file
        
        tmpHtml = tmpHtml.replace("<!--[[[HEADCONTENT]]]-->",str(self.injectScript()))
        tmpHtml = tmpHtml.replace("<!--[[[BODYCONTENT]]]-->",str(self.injectContent()))
        
        try:
            try:
                #TODO: Fix hardcoded path
                f = open(self.tmpPath,'w')
                f.write(tmpHtml)
                tmpHtml = None
            finally:
                f.close()
        except:
            # TODO: Fix hardcoded path
            self.log.log(0,"error","Unable to write " + self.tmpPath)
            self.parent.next()
            return
        
        # Navigate the browser to the temporary file
        self.p.enqueue('browserNavigate',(self.mediaNodeName,"file://" + os.path.abspath(self.tmpPath),self.finishedRendering))

    def requiredFiles(self):
        return []
	
    def timerElapsed(self):
        # TODO: This shouldn't be required. When media is finally disposed properly then the file should be deleted
        # as part of the dispose method.
        try:
            os.remove(self.tmpPath)
        except:
            log.log(0,"error","Unable to delete file %s" % (self.tmpPath))  
        self.parent.next()
	
    def dispose(self):
        self.p.enqueue('del',self.mediaNodeName)
        try:
            os.remove(self.tmpPath)
        except:
            self.log.log(0,"error","Unable to delete file %s" % (self.tmpPath))
        self.parent.tNext()
    
    def injectContent(self):
        """ Returns a string of content to inject in to the page """
        return ""
    
    def injectScript(self):
        """ Returns a string of script to inject in to the page """
        return ""
    
    def browserOptions(self):
        """ Return a tuple of options for the Browser component. True/False/None. None makes no change to the
        current state. True sets to on, False sets to off. Options order is:
            Transparency,Scrollbars
        """
        return (False,False)
    
    def finishedRendering(self):
        optionsTuple = (self.mediaNodeName,True,False)
        self.p.enqueue('browserOptions',optionsTuple)
        self.p.enqueue('setOpacity',(self.mediaNodeName,1))
        # TODO: This next line should really callback self.parent.next. See timerElapsed function
        self.p.enqueue('timer',(int(self.duration) * 1000,self.timerElapsed))
