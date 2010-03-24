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

class FlashMedia(BrowserMediaBase):
        
    def injectContent(self):
        """ Returns a string of content to inject in to the page """
        content = ""
        
        swfURI = "file://" + os.path.abspath(os.path.join(self.libraryDir,self.options['uri']))
        
        content += '<centre>\n'
        content += '<object width="%d" height="%d">\n' % (self.width ,self.height)
        content += '  <param name="movie" value="%s">\n' % swfURI
        content += '  <embed wmode="transparent" type="application/x-shockwave-flash" src="%s" width="%d" height="%d">\n' % (swfURI,self.width,self.height)
        content += '  </embed>\n'
        content += '</object>\n'
        content += '</centre>\n'
        
        return content
    
    def injectScript(self):
        return ""
    
    def browserOptions(self):
        """ Return a tuple of options for the Browser component. True/False/None. None makes no change to the
        current state. True sets to on, False sets to off. Options order is:
            Transparency,Scrollbars
        """
        return (True,None)
    
