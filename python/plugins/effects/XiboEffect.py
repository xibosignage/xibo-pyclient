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

from threading import Thread

class XiboEffect(Thread):
    "Abstract Class - Interface for Effects"
    def __init__(self,log,player,media,node,callback=None):
        Thread.__init__(self)
        log.log(2,"info",self.__class__.__name__ + " plugin loaded!")
        self.log = log
        self.p = player
        self.media = media
        self.callback = callback
        self.node = node
        self.options = {}

        # Get all the options from the effects node
        attrs = self.node.attributes
        for attrName in attrs.keys():
            attrNode = attrs.get(attrName)
            attrValue = attrNode.nodeValue
            self.options[attrName] = attrValue

    def run(self):
        if self.callback != None:
            try:
                self.callback()
            except:
                self.log.log(0,"error","Exception thrown calling the callback " + self.callback)
