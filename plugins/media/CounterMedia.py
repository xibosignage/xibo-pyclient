#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# Xibo - Digitial Signage - http://www.xibo.org.uk
# Copyright (C) 2011 Alex Harrington
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

from BrowserMediaAnimatedBase import BrowserMediaAnimatedBase
from threading import Thread

class CounterMedia(BrowserMediaAnimatedBase):

    def __setupMedia__(self,log,config,parent,player,mediaNode):
        log.log(6,"info",self.__class__.__name__ + " plugin loaded!")
        self.log = log
        self.parent = parent
        self.config = config
        self.p = player
        self.mediaNode = mediaNode
        self.mediaNodeName = None
        self.mediaType = None
        self.duration = None
        self.schemaVersion = None
        self.invalid = False
        self.options = {}
        self.rawNode = None
        self.optionsNode = None
        try:
            self.scaleFactor = self.parent.parent.l.scaleFactor
        except:
            self.scaleFactor = 1.0
        
        self.libraryDir = os.path.abspath(self.config.get('Main','libraryDir'))

        if self.p == None:
            self.regionNodeName = 'null'
            self.regionNodeNameExt = 'null'
            self.width = '10'
            self.height = '10'
            self.mediaNodeNameExt = '-null'
        else:
            self.regionNodeName = self.parent.regionNodeName
            self.regionNodeNameExt = self.parent.regionNodeNameExt
            self.width = self.parent.width
            self.height = self.parent.height
            self.mediaNodeNameExt = str(self.p.nextCounterId())

        # Calculate the media ID name
        try:
            self.mediaId = str(self.mediaNode.attributes['id'].value)
            self.mediaNodeName = "counter" + self.mediaNodeNameExt
        except KeyError:
            log.log(1,"error",_("Media XLF is invalid. Missing required id attribute"))
            self.mediaNodeName = "M-invalid-" + self.regionNodeNameExt + self.mediaNodeNameExt
            self.invalid = True
            return

        # Calculate the media type
        try:
            self.mediaType = str(self.mediaNode.attributes['type'].value)
        except:
            log.log(1,"error",_("Media XLF is invalid. Missing required type attribute"))
            self.invalid = True
            return

        # Calculate the media duration
        try:
            self.duration = str(self.mediaNode.attributes['duration'].value)
        except KeyError:
            log.log(1,"error",_("Media XLF is invalid. Missing required duration attribute"))
            self.invalid = True
            return

        # Find the options and raw nodes and assign them to self.rawNode and self.optionsNode
        for cn in self.mediaNode.childNodes:
            if cn.nodeType == cn.ELEMENT_NODE and cn.localName == "options":
                self.optionsNode = cn
            if cn.nodeType == cn.ELEMENT_NODE and cn.localName == "raw":
                self.rawNode = cn

        # Parse the options block in to the self.options[] array:
        for cn in self.optionsNode.childNodes:
            if cn.localName != None:
                try:
                    self.options[str(cn.localName)] = cn.childNodes[0].nodeValue
                    log.log(5,"info","Media Options: " + str(cn.localName) + " -> " + str(cn.childNodes[0].nodeValue))
                except IndexError:
                    # Some options are allowed to be empty. Ignore these.
                    self.options[str(cn.localName)] = ""

        # Parse the effects block
        self.effects = self.mediaNode.getElementsByTagName('effect')

        if self.p != None:
            if str(self.options['popupNotification']) == '1':
                self.p.ticketOSD = True
            else:
                self.p.ticketOSD = False


    def injectContent(self):
        # Parse out the template element from the raw tag.
        try:
            for t in self.rawNode.getElementsByTagName('template'):
                self.templateNode = t
        
            for node in self.templateNode.childNodes:
                if node.nodeType == node.CDATA_SECTION_NODE:
                    self.template = node.data.strip()
                    self.log.log(5,'audit','Template is: ' + self.template)
        except:
            self.log.log(2,'error','%s Error parsing out the template from the xlf' % self.mediaNodeName)
            return ''

        # Replace the template [Counter] tag:
        self.text = self.template.replace("[Counter]", '<span id="Counter">C</span>')
        self.text = self.text.replace("[counter]", '<span id="Counter">C</span>')

        return self.text

    def injectScript(self):
        js = "<script type='text/javascript'>\n\n"
        js += "function updateCounter(number) {\n"
        js += "  document.getElementById('Counter').innerHTML = number;\n"
        js += "}\n"
        js += "</script>\n\n"

        return js

    def finishedRendering(self):
        bo = self.browserOptions()
        optionsTuple = (self.mediaNodeName,bo[0],bo[1])
        self.p.enqueue('browserOptions',optionsTuple)
        self.p.enqueue('executeJavascript',(self.mediaNodeName,"updateCounter('%s');" % self.p.counterValue))
        self.p.enqueue('setOpacity',(self.mediaNodeName,1))
        # TODO: This next line should really callback self.parent.next. See timerElapsed function
        self.p.enqueue('timer',(int(self.duration) * 1000,self.timerElapsed))
