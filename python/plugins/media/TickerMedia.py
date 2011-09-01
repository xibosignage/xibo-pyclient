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
import sys, os, time, codecs
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

        self.feed = feedparser.parse(os.path.join(self.libraryDir, self.mediaId) + '-cache.xml')
        self.log.log(5,"audit","Feed parsed")

        if self.feed != None:
            
            # Build some kind of array of items that are feed specific to replace
            feedDetails = []
            try:
                feedDetails.append(('FeedLastBuildDate',self.feed['feed']['lastbuilddate']))
            except:
                feedDetails.append(('FeedLastBuildDate',u''))
            
            try:
                feedDetails.append(('FeedSubtitle',self.feed['feed']['subtitle']))
            except:
                feedDetails.append(('FeedSubtitle',u''))
            
            try:
                feedDetails.append(('FeedLanguage',self.feed['feed']['language']))
            except:
                feedDetails.append(('FeedLanguage',u''))
            
            try:
                feedDetails.append(('FeedLink',self.feed['feed']['link']))
            except:
                feedDetails.append(('FeedLink',u''))
            
            try:
                feedDetails.append(('FeedTitle',self.feed['feed']['title']))
            except:
                feedDetails.append(('FeedTitle',u''))
            
            try:
                feedDetails.append(('FeedVersion',self.feed['feed']['version']))
            except:
                feedDetails.append(('FeedVersion',u''))
            
            try:
                feedDetails.append(('FeedEncoding',self.feed['feed']['encoding']))
            except:
                feedDetails.append(('FeedEncoding',u''))
            
            for item in self.feed['entries']:
                # Copy the array above and add in item specific items
                itemDetails = []
                
                try:
                    itemDetails.append(('Description',item['description']))
                except:
                    itemDetails.append(('Description',u''))
                    
                try:
                    itemDetails.append(('Title',item['title']))
                except:
                    itemDetails.append(('Title',u''))
                
                try:
                    itemDetails.append(('Link',item['link']))
                except:
                    itemDetails.append(('Link',u''))
                    
                try:
                    itemDetails.append(('Summary',item['summary']))
                except:
                    itemDetails.append(('Summary',u''))
                    
                try:
                    itemDetails.append(('Author',item['author']))
                except:
                    itemDetails.append(('Author',u''))
                
                try:
                    itemDetails.append(('Date',item['updated_parsed']))
                except:
                    try:
                        itemDetails.append(('Date',item['updated']))
                    except:
                        itemDetails.append(('Date',u''))
                
                # Get a copy of the item template (from XLF)
                tmpItem = self.template
                
                # Loop over the array and attempt to replace each key in tmpItem
                for field in itemDetails:
                    if field[0] == 'Date':
                        try:
                            field = (field[0],time.strftime(self.config.get('TickerMedia','dateFormat'),field[1]))
                        except:
                            pass
                    tmpItem = tmpItem.replace("[%s]" % field[0], field[1])
                
                for field in feedDetails:
                    tmpItem = tmpItem.replace("[%s]" % field[0], field[1])

                content.append(tmpItem)

            if not self.options.has_key('numItems'):
                self.options['numItems'] = '';

            if not self.options.has_key('takeItemsFrom'):
                self.options['takeItemsFrom'] = 'start';

            try:
                if not self.options['numItems'] == '':
                    numItems = int(self.options['numItems'])

                    if self.options['takeItemsFrom'] == 'start':
                        content = content[:numItems]
                    else:
                        content = content[(0 - numItems):]

            except:
                pass
                
        return content
        
    def download(self):
        
        tries = 3
        i = 0
        flag = False
        
        # If libraryDir/self.mediaId-cache.xml exists then check if it's too old to use
        try:
    	    mtime = os.path.getmtime(os.path.join(self.libraryDir,self.mediaId + '-cache.xml'))
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
                self.log.log(1,"error",_("Unable to load from URL %s") %  self.options['uri'])
            i += 1
        
        if flag:
            try:
                try:
                    f = open(os.path.join(self.libraryDir,self.mediaId) + '-cache.xml','w')
                    f.write(s)
                finally:
                    f.close()
            except:
                self.log.log(0,"error",_("Unable to write %s") % os.path.join(self.libraryDir,self.mediaId) + '-cache.xml')

