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
        self.template = None
        self.log.log(5,"audit","RSS Ticker starting")
        self.log.log(5,"audit","URI: " + self.options['uri'])

        self.download()
        
        # Parse out the template element from the raw tag.
        try:
            for t in self.rawNode.getElementsByTagName('template'):
                self.templateNode = t
        
            for node in self.templateNode.childNodes:
                if node.nodeType == node.CDATA_SECTION_NODE:
                    self.template = node.data.encode('UTF-8')
                    self.log.log(5,'audit','Template is: ' + self.template)
        except IOError:
            self.log.log(2,'error','%s Error parsing out the template from the xlf' % self.mediaNodeName)
            return

        # TODO: Fix the hardcoded path
        self.feed = feedparser.parse(os.path.join("data", self.mediaId + '-cache.xml'))
        self.log.log(5,"audit","Feed parsed")

        if self.feed != None:
            self.log.log(5,"audit","Feed title: " + self.feed['feed']['title'])
            
            # Build some kind of array of items that are feed specific to replace
            feedDetails = []
            try:
                feedDetails.append(('FeedLastBuildDate',self.feed['feed']['lastbuilddate']))
            except:
                feedDetails.append(('FeedLastBuildDate',''))
            
            try:
                feedDetails.append(('FeedSubtitle',self.feed['feed']['subtitle']))
            except:
                feedDetails.append(('FeedSubtitle',''))
            
            try:
                feedDetails.append(('FeedLanguage',self.feed['feed']['language']))
            except:
                feedDetails.append(('FeedLanguage',''))
            
            try:
                feedDetails.append(('FeedLink',self.feed['feed']['link']))
            except:
                feedDetails.append(('FeedLink',''))
            
            try:
                feedDetails.append(('FeedTitle',self.feed['feed']['title']))
            except:
                feedDetails.append(('FeedTitle',''))
            
            try:
                feedDetails.append(('FeedVersion',self.feed['feed']['version']))
            except:
                feedDetails.append(('FeedVersion',''))
            
            try:
                feedDetails.append(('FeedEncoding',self.feed['feed']['encoding']))
            except:
                feedDetails.append(('FeedEncoding',''))
            
            for item in self.feed['entries']:
                # Copy the array above and add in item specific items
                itemDetails = feedDetails
                
                try:
                    itemDetails.append(('Description',item['description']))
                except:
                    itemDetails.append(('Description',''))
                    
                try:
                    itemDetails.append(('Title',item['title']))
                except:
                    itemDetails.append(('Title',''))
                
                try:
                    itemDetails.append(('Link',item['link']))
                except:
                    itemDetails.append(('Link',''))
                    
                try:
                    itemDetails.append(('Summary',item['summary']))
                except:
                    itemDetails.append(('Summary',''))
                    
                try:
                    itemDetails.append(('Author',item['author']))
                except:
                    itemDetails.append(('Author',''))
                
                try:
                    itemDetails.append(('Date',item['updated']))
                except:
                    itemDetails.append(('Date',''))
                
                # Get a copy of the item template (from XLF)
                tmpItem = self.template
                
                # Loop over the array and attempt to replace each key in tmpItem
                for field in itemDetails:
                    print "RSS Modifying [%s]" % field[0]
                    tmpItem = tmpItem.replace("[%s]" % field[0], str(field[1]))
                    print "RSS Output: %s" % tmpItem
                
                if self.options['direction'] == 'left' or self.options['direction'] == 'right':
                    tmpItem = tmpItem.replace('<p>','')
                    tmpItem = tmpItem.replace('</p>','')
                    
                    tmpItem = "<span class='article' style='padding-left:4px;'>%s</span>" % tmpItem
                    tmpItem += "<span style='padding-left:4px;'> - </span>"
                else:
                    tmpItem = "<div class='XiboRssItem' style='display:block;padding:4px;width:%d'>%s</div>" % (self.width - 10,tmpItem)
                
                content += tmpItem
        
        textWrap = ""
        
        if self.options['direction'] == 'none':
            pass
        else:
            if self.options['direction'] == 'left' or self.options['direction'] == 'right':
                textWrap = "white-space: nowrap";
                content = "<nobr>%s</nobr>" % content
            else:
                textWrap = "width: %dpx;" % (self.width - 50);
            
            if self.options['direction'] == 'single':
                content = "<div id='text'>%s</div>" % content
            else:
                content = "<div id='text' style='position:relative;overflow:hidden;width:%dpx; height:%dpx;'><div id='innerText' style='position:absolute; left: 0px; top: 0px; %s'>%s</div></div>" % (self.width - 10,self.height, textWrap, content)
                
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
    
    def browserOptions(self):
        """ Return a tuple of options for the Browser component. True/False/None. None makes no change to the
        current state. True sets to on, False sets to off. Options order is:
            Transparency,Scrollbars
        """
        return (True,False)
    
    def download(self):
        print "*** DOWNLOAD CALLED ***"
        
        tries = 3
        i = 0
        flag = False
        
        # If data/self.mediaId-cache.xml exists then check if it's too old to use
        # TODO: This needs to be tested.
        try:
    	    mtime = os.path.getmtime(os.path.join('data',self.mediaId + '-cache.xml'))
            if time.time() < (mtime + (self.options['cacheTimeout'] * 60)):
                print "*** CACHE IS FRESH ***"
                return
        except:
            # File probably doesn't exist. Do nothing.
            pass
        
        print "*** CACHE IS STALE ***"
        
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

