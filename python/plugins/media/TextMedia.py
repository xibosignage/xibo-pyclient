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

from XiboMedia import XiboMedia
from threading import Thread
from HTMLParser import HTMLParser

class TextMedia(XiboMedia):
    def add(self):
        tmpXML = '<div id="' + self.mediaNodeName + '" opacity="1" />'
        self.p.enqueue('add',(tmpXML,self.regionNodeName))
    
    def run(self):
        
        html = "<p>Empty HTML Text Node</p>"
        
        # Parse out the text element from the raw tag.
        text = self.rawNode.getElementsByTagName('text')
        for t in text:
            self.textNode = t
        
        for node in self.textNode.childNodes:
            if node.nodeType == node.CDATA_SECTION_NODE:
                # TODO: This should accept unicode encoded text. The str() casting is wrong. No idea why it doesn't work.
                html = str(node.data)
                self.log.log(7,'audit','HTML to display is: ' + html)
        
        parser = HTMLPango()
        parser.feed(html)
        tmpXML = '<words id="' + self.mediaNodeName + 'T1" opacity="1" parawidth="' + str(self.getWidth()) + '">' + parser.getPango() + '</words>'
        self.p.enqueue('add',(tmpXML,self.mediaNodeName))
        self.p.enqueue('timer',(int(self.duration) * 1000,self.parent.next))
        print(parser.getPango())
    
    def dispose(self):
        self.p.enqueue('del',self.mediaNodeName)
        self.parent.tNext()
        
class HTMLPango(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.outputStr = ""
        self.hasOutput = False

    def handle_starttag(self, tag, attrs):
        # print(tag)
        if tag == "span":
            # print(attrs)
            for i in attrs:
                if i[0] == "style":
                    tmpStyle = i[1].split(':')
                    if tmpStyle[0] == 'font-size':
                        size = tmpStyle[1].split('em;')[0].strip()
                        size = float(size) * 1024 * 12
                        size = int(size)
                        self.output('<span size="' + str(size) + '">')
                    if tmpStyle[0] == 'font-family':
                        face = tmpStyle[1].split(';')[0].strip()
                        self.output('<span face="' + str(face) + '">')
                    if tmpStyle[0] == 'color':
                        color = tmpStyle[1].split(';')[0].strip()
                        if color.find('rgb(') != -1:
                            color.strip()
                            # Remove leading rgb
                            # Leaves (255, 255, 255)
                            color = color[3:]
                            rgb = tuple(int(s) for s in color[1:-1].split(','))
                            color = self.RGBToHTMLColor(rgb)
                            # self.output('<span color="' + color + '">')
                            self.output('<span>')
        elif tag == "b":
            self.output('<b>')
        elif tag == "i":
            self.output('<i>')
        elif tag == "u":
            self.output('<u>')
        elif tag == "strike":
            self.output('<s>')
        elif tag == "sup":
            self.output('<sup>')
        elif tag == "sub":
            self.output('<sub>')
        elif tag == "big":
            self.output('<big>')
        elif tag == "small":
            self.output('<small>')
        elif tag == "tt" or tag == "pre":
            self.output('<tt>')
        elif tag == "p":
            if self.hasOutput:
                # TODO: Broken
                self.output("\n\n")
        elif tag == "br":
            # Handled by the close tag.
            pass
        elif tag == "div":
            # TODO: Broken
            self.output("\n")
    
    def handle_endtag(self, tag):
        if tag == "span":
            self.output('</span>')
        elif tag == "b":
            self.output('</b>')
        elif tag == "i":
            self.output('</i>')
        elif tag == "u":
            self.output('</u>')
        elif tag == "strike":
            self.output('</s>')
        elif tag == "sup":
            self.output('</sup>')
        elif tag == "sub":
            self.output('</sub>')
        elif tag == "big":
            self.output('</big>')
        elif tag == "small":
            self.output('</small>')
        elif tag == "tt" or tag == "pre":
            self.output('</tt>')
        elif tag == "br":
            # TODO: Broken
            self.output("\n")

    
    def handle_data(self, data):
        # print("Encountered data " + data ) 
        self.output(data)   

    # From ActivState Recipies: http://code.activestate.com/recipes/266466/        
    def RGBToHTMLColor(self, rgb_tuple):
        """ convert an (R, G, B) tuple to #RRGGBB """
        hexcolor = '#%02x%02x%02x' % rgb_tuple
        # that's it! '%02x' means zero-padded, 2-digit hex values
        return hexcolor

    def output(self, pango):
        self.hasOutput = True
        self.outputStr += pango

    def getPango(self):
        return self.outputStr
