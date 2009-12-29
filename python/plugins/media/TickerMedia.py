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

from BrowserMediaAnimatedBase import BrowserMediaAnimatedBase
from threading import Thread
import urllib
import sys, os, time
import feedparser

class TickerMedia(BrowserMediaAnimatedBase):
        
    def getContent(self):
        """ Returns a string of content items to inject in to the page """
        content = []
        
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
        except:
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
                itemDetails = []
                
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
                    tmpItem = tmpItem.replace("[%s]" % field[0], str(field[1]))
                
                for field in feedDetails:
                    tmpItem = tmpItem.replace("[%s]" % field[0], str(field[1]))

                
                content.append(tmpItem)
                                
        return content
        
    def download(self):
        
        tries = 3
        i = 0
        flag = False
        
        # If data/self.mediaId-cache.xml exists then check if it's too old to use
        # TODO: This needs to be tested.
        try:
    	    mtime = os.path.getmtime(os.path.join('data',self.mediaId + '-cache.xml'))
            if time.time() < (mtime + (int(self.options['updateInterval']) * 60)):
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

