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
import sys, os, time

class BrowserMediaAnimatedBase(BrowserMediaBase):
        
    def injectContent(self):
        """ Returns a string of content to inject in to the page """
        content = ""
        
        items = self.getContent()
        count = 0
        
        for tmpItem in items:
            count += 1
            if self.options['direction'] == 'left' or self.options['direction'] == 'right':
                tmpItem = tmpItem.replace('<p>','')
                tmpItem = tmpItem.replace('</p>','')
                tmpItem = tmpItem.replace('<p/>','')
                tmpItem = tmpItem.replace('<br>','')
                tmpItem = tmpItem.replace('<br/>','')
                tmpItem = tmpItem.replace('<div>','')
                tmpItem = tmpItem.replace('</div>','')
                tmpItem = tmpItem.replace('<div/>','')
                
                tmpItem = "<span class='article' style='padding-left:4px;'>%s</span>" % tmpItem
            else:
                tmpItem = "<div class='XiboRssItem' style='display:block;padding:4px;width:%dpx'>%s</div>" % (self.width - 10,tmpItem)
            
            content += tmpItem
        
        self.itemCount = count

        # Add in the Copyright Text (if applicable)
        try:
            content += self.options['copyright']
        except:
            pass
        
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

        if self.options.has_key('direction'):
            if self.options['direction'] == "":
                self.options['direction'] = 'none'
        else:
            self.options['direction'] = 'none'

        if self.options.has_key('scrollSpeed'):
            if self.options['scrollSpeed'] == "":
                self.options['scrollSpeed'] = '30'
        else:
            self.options['scrollSpeed'] = '30'

        if self.options.has_key('durationIsPerItem'):
            if self.options['durationIsPerItem'] == "":
                self.options['durationIsPerItem'] = '0'
        else:
            self.options['durationIsPerItem'] = '0';
        
        if not self.scaleFactor == 0:
            s = self.options['scrollSpeed']
            self.options['scrollSpeed'] = str(int(int(self.options['scrollSpeed']) * 2 * (1.0/self.scaleFactor)))
#            print "*** REFACTORED SCROLL SPEED FROM %s to %s ***" % (s,self.options['scrollSpeed'])
            
        js = ""
        
        # Multiply out the duration if duration is per item.
        if not self.options['durationIsPerItem'] == '0':
            if self.itemCount > 0:
                self.duration = int(self.duration) * self.itemCount
        
        if self.options['direction'] == "single":
            js = "<script type='text/javascript'>\n\n"
            js += "function init() {\n"
            js += "  var totalDuration = %d * 1000;\n" % int(self.duration)
            js += "  var itemCount = $('.XiboRssItem').size();\n"
            js += "  var itemTime = totalDuration / itemCount;\n"
            js += "  if (itemTime < 2000) itemTime = 2000;\n"
            js += "  // Try to get the itemTime from an element we expect to be in the HTML\n"
            js += "  $('#text').cycle({fx: 'fade', timeout: itemTime, cleartypeNoBg:true});\n"
            js += "  }\n"
            js += "</script>\n\n"
        elif self.options['direction'] == "none":
            pass
        else:
            js = "<script type='text/javascript'>\n\n"
            js += "function init() {\n"
            js += "  tr = new TextRender('text', 'innerText', '" + self.options['direction'] + "', 2);\n"
            js += "  var timer = 0;\n"
            js += "  timer = setInterval('tr.TimerTick()', " + str(self.options['scrollSpeed']) + ");\n"
            js += "}"
            js += "</script>\n\n"
        
        js += "<style type='text/css'>body { font-size:%fem; }</style>\n\n" % self.scaleFactor
        return js
    
    def browserOptions(self):
        """ Return a tuple of options for the Browser component. True/False/None. None makes no change to the
        current state. True sets to on, False sets to off. Options order is:
            Transparency,Scrollbars
        """
        return (True,False)
    
    def getContent(self):
        return []
