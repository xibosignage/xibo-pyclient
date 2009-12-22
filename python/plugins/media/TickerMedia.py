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

sys.path.append('./FeedParser')
import feedparser

class TickerMedia(BrowserMediaBase):
        
    def injectContent(self):
        """ Returns a string of content to inject in to the page """
        content = ""
        
        self.options['cacheTimeout'] = 20
        self.options['uri'] = urllib.unquote(self.options['uri'])
        
        self.feed = None
        self.log.log(5,"audit","RSS Ticker starting")
        self.log.log(5,"audit","URI: " + self.options['uri'])

        self.download()

        # TODO: Fix the hardcoded path
        self.feed = feedparser.parse(os.path.join("data", self.mediaId + '-cache.xml'))
        self.log.log(5,"audit","Feed parsed")

        if self.options['direction'] == "single":
            pass
        else:
            content += "<div id='text' style='position:relative;overflow:hidden;width:" + str(self.width) + "px; height:" + str(self.height) + "px;'>"
            content += "<div id='innerText' style='position:absolute; left: 0px; top: 0px; white-space: nowrap'><nobr>"

        if self.feed != None:
            self.log.log(5,"audit","Feed title: " + self.feed['feed']['title'])
            for item in self.feed['entries']:
                # TODO: Need to format the items
                content += "<span class='article' style='padding-left:4px;'>%s</span>" % (item.description)
        
        if self.options['direction'] == 'single':
            pass
        else:
            content += "</nobr></div></div>"
        
        return content
    
    def injectScript(self):
        """ Returns a string of script to inject in to the page """
        if self.options['direction'] == "single":
            js = ""
        else:
            js = "<script type='text/javascript'>\n\n"
            js += "function init() {\n"
            js += "  tr = new TextRender('text', 'innerText', '" + self.options['direction'] + "');\n"
            js += "  var timer = 0;\n"
            js += "  timer = setInterval('tr.TimerTick()', " + str(self.options['scrollSpeed']) + ");\n"
            js += "}"
            js += "</script>\n\n"
            js += "<style type='text/css'>html {overflow:hidden;}</style>"
        return js
    
    """ <style type='text/css'>body {background-color:#000000;}, p, h1, h2, h3, h4, h5 { margin:2px; font-size:2.1em; }</style> """
    
    def browserOptions(self):
        """ Return a tuple of options for the Browser component. True/False/None. None makes no change to the
        current state. True sets to on, False sets to off. Options order is:
            Transparency,Scrollbars
        """
        return (True,False)
    
    def download(self):
        tries = 3
        i = 0
        flag = False
        
        # If data/self.mediaId-cache.xml exists then check if it's too old to use
        # TODO: This needs to be tested.
        try:
    	    mtime = os.path.getmtime(os.path.join('data',self.mediaId + '-cache.xml'))
            if time.time() < (mtime + (self.options['cacheTimeout'] * 60)):
                return
        except:
            # File probably doesn't exist. Do nothing.
            pass
        
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
                self.log.log(1,"error",_("Unable to load from URL %s") %  self.options['uri'])
        
        if flag:
            try:
                try:
                    #TODO: Fix hardcoded path
                    f = open(os.path.join('data',self.mediaId + '-cache.xml'),'w')
                    f.write(s)
                finally:
                    f.close()
            except:
                # TODO: Fix hardcoded path
                self.log.log(0,"error",_("Unable to write %s") % os.path.join('data',self.mediaId + '-cache.xml'))

