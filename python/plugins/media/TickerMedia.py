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

import os
import time
import sys
import urllib

from XiboMedia import XiboMedia
from threading import Thread

sys.path.append('./FeedParser')
import feedparser

class TickerMedia(XiboMedia):
    def add(self):
        tmpXML = '<div id="' + self.mediaNodeName + '" />'
        self.p.enqueue('add',(tmpXML,self.regionNodeName))
        tmpXML = '<words id="' + self.mediaNodeName + '-loading" opacity="1" font="Arial" color="000000" size="12" text="Loading..." />'
        self.p.enqueue('add',(tmpXML,self.mediaNodeName))
            	
    def requiredFiles(self):
        return []
    
    def run(self):
        self.p.enqueue('setOpacity',(self.mediaNodeName,1))
        
        # Insert a cacheTimeout field to options.
        # This should become part of the XLF in the future.
        self.options['cacheTimeout'] = 20
        self.options['uri'] = urllib.unquote(self.options['uri'])
        
        self.feed = None
        self.log.log(0,"info","RSS Ticker starting")
        self.log.log(0,"info","URI: " + self.options['uri'])

        # If data/self.mediaId-cache.xml exists then check if it's too old to use
        # TODO: This is broken!
        #if os.path.exists('data' + os.sep + self.mediaId + '-cache.xml'):
    	#    file_stats = os.stat('data' + os.sep + self.mediaId + '-cache.xml')
    	#    mtime = file_stats[ST_MTIME]
        #    if time.ctime() > (mtime + (self.options['cacheTimeout'] * 60)):
        #        pass
        #    else:
        #        self.download()
        #else:
        #    self.download()
        
        # TODO: Remove this line when above fixed.
        self.download()

        self.feed = feedparser.parse('data' + os.sep + self.mediaId + '-cache.xml')
        self.log.log(0,"info","Feed parsed")

        if self.feed != None:
            self.log.log(0,"info","Feed title: " + self.feed['feed']['title'])
            tmpXML = '<words id="' + self.mediaNodeName + '-content" opacity="1" font="Arial" color="000000" size="12">'
            tmpXML += str(self.feed['feed']['title']) + "</words>"
            self.p.enqueue('del',self.mediaNodeName + '-loading')
            self.p.enqueue('add',(tmpXML, self.mediaNodeName))
        
        self.p.enqueue('timer',(int(self.duration) * 1000,self.parent.next))

	   
    def download(self):
        tries = 3
        i = 0
        flag = False
        
        while i < tries and flag == False:
            try:
                try:
                    f = urllib.urlopen(self.options['uri'])
                    s = f.read()
                    flag = True
                finally:
                    f.close()
            except:
                tries =+ 1
                self.log.log(1,"error","Unable to load from URL " + self.options['uri'])
        
        if flag:
            try:
                try:
                    f = open("data" + os.sep + self.mediaId + '-cache.xml','w')
                    f.write(s)
                finally:
                    f.close()
            except:
                self.log.log(0,"error","Unable to write data/" + self.mediaId + "-cache.xml")

    def dispose(self):
        self.p.enqueue('del',self.mediaNodeName)
        self.parent.tNext()
