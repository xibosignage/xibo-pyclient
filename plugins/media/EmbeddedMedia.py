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

from BrowserMediaBase import BrowserMediaBase
from threading import Thread
import urllib
import sys, os

class EmbeddedMedia(BrowserMediaBase):
        
    def injectContent(self):
        """ Returns a string of content to inject in to the page """
        content = ""
        
        # Parse out the embedHtml element from the raw tag.
        try:
            for t in self.rawNode.getElementsByTagName('embedHtml'):
                self.embedHtmlNode = t
        
            for node in self.embedHtmlNode.childNodes:
                if node.nodeType == node.CDATA_SECTION_NODE:
                    content = node.data.encode('UTF-8')
                    self.log.log(5,'audit','EmbeddedHTML is: ' + content)
        except:
            self.log.log(2,'error','%s: Error parsing out the embedHtml from the xlf' % self.mediaNodeName)
        
        return content
    
    def injectScript(self):
        """ Returns a string of script to inject in to the page """
        script = ""
        
        # Parse out the embedHtml element from the raw tag.
        try:
            for t in self.rawNode.getElementsByTagName('embedScript'):
                self.embedScriptNode = t
        
            for node in self.embedScriptNode.childNodes:
                if node.nodeType == node.CDATA_SECTION_NODE:
                    script = node.data.encode('UTF-8')
                    self.log.log(5,'audit','EmbeddedScript is: ' + script)
        except:
            self.log.log(2,'error','%s: Error parsing out the embedScript from the xlf' % self.mediaNodeName)
        
        return script
    
    def browserOptions(self):
        """ Return a tuple of options for the Browser component. True/False/None. None makes no change to the
        current state. True sets to on, False sets to off. Options order is:
            Transparency,Scrollbars
        """
        return (True,None)
    
