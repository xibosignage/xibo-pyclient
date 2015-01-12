#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# Xibo - Digitial Signage - http://www.xibo.org.uk
# Copyright (C) 2009-14 Alex Harrington
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

from XiboMedia import XiboMedia
from threading import Thread
import os

class VideoMedia(XiboMedia):
    def add(self):
        video = os.path.join(self.libraryDir,self.options['uri'])
        
        if self.parent.numNodes == 1:
            if self.config.getboolean('VideoMedia', 'loop'): 
                loop = '1'
            else:
                loop = '0'
        else:
            loop = '0'
            
                 
        tmpXML = str('<video href="%s" id="%s" opacity="0" loop="%s" />' % (video,self.mediaNodeName,loop))
        self.p.enqueue('add',(tmpXML,self.regionNodeName))

    def run(self):
        self.p.enqueue('play', self.mediaNodeName)
        self.p.enqueue('resize',(self.mediaNodeName, self.width, self.height,'centre','centre'))
        self.p.enqueue('setOpacity',(self.mediaNodeName,1))
        if int(self.duration) > 0:
            self.p.enqueue('timer',(int(self.duration) * 1000,self.parent.next))
        else:
            self.p.enqueue('eofCallback',(self.mediaNodeName,self.parent.next))

        self.startStats()

    def requiredFiles(self):
        return [str(self.options['uri'])]
    
    def dispose(self):
        self.returnStats()
        self.p.enqueue('del',self.mediaNodeName)
        self.parent.tNext()
