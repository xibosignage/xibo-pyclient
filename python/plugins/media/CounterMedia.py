#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# Xibo - Digitial Signage - http://www.xibo.org.uk
# Copyright (C) 2010 Alex Harrington
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

    def getContent(self):
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
            return []

        # Replace the template [Counter] tag:
        self.text = self.template.replace("[Counter]", '<div id="Counter">C</div>')
        self.text = self.template.replace("[counter]", '<div id="Counter">C</div>')

        return [self.text]

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
        self.p.enqueue('executeJavascript',(self.mediaNodeName,"updateCounter(5);"))
        self.p.enqueue('setOpacity',(self.mediaNodeName,1))
        # TODO: This next line should really callback self.parent.next. See timerElapsed function
        self.p.enqueue('timer',(int(self.duration) * 1000,self.timerElapsed))
