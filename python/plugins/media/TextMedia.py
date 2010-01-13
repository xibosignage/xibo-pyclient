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

class TextMedia(BrowserMediaAnimatedBase):
    def getContent(self):
        
        # Parse out the text element from the raw tag.
        try:
            for t in self.rawNode.getElementsByTagName('text'):
                self.textNode = t
        
            for node in self.textNode.childNodes:
                if node.nodeType == node.CDATA_SECTION_NODE:
                    self.text = node.data.strip()
                    self.log.log(5,'audit','Text is: ' + self.text)
        except:
            self.log.log(2,'error','%s Error parsing out the text from the xlf' % self.mediaNodeName)
            return []
        
        return [self.text]
