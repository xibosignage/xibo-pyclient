#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# Xibo - Digitial Signage - http://www.xibo.org.uk
# Copyright (C) 2009-13 Alex Harrington
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

from VideoMedia import VideoMedia
from threading import Thread
import os
import urllib

class LocalvideoMedia(VideoMedia):
    def add(self):
        video = urllib.unquote(self.options['uri'])
        
        if self.parent.numNodes == 1:
            if self.config.getboolean('VideoMedia', 'loop'): 
                loop = '1'
            else:
                loop = '0'
        else:
            loop = '0'
        
        tmpXML = str('<video href="%s" id="%s" opacity="0" loop="%s" />' % (video,self.mediaNodeName,loop))
        self.p.enqueue('add',(tmpXML,self.regionNodeName))

    def requiredFiles(self):
        # We have to assume that the video will be where it's supposed to be!
        return []
