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

from XiboMedia import XiboMedia
from threading import Thread
import os
from libavg import avg
from PIL import Image

class ImageMedia(XiboMedia):
    def add(self):

        tmpXML = '<image id="' + self.mediaNodeName + '" opacity="0" />'
        self.p.enqueue('add',(tmpXML,self.regionNodeName))
        
        w = int(self.width) + 1
        h = int(self.height) + 1
        fName = os.path.join(self.libraryDir,self.options['uri'])
        thumb = os.path.join(self.libraryDir,'scaled',self.options['uri']) + "-%dx%d" % (w,h)
        if not os.path.exists(thumb) or (os.path.getmtime(thumb) < os.path.getmtime(fName)):
            self.log.log(3,'info',_("%s: Resizing image %s to %dx%d") % (self.mediaNodeName,self.options['uri'],w,h))
            image = Image.open(fName)
            image.thumbnail((w,h),Image.ANTIALIAS)
            image.save(thumb, image.format)
            del image

        bitmap = avg.Bitmap(thumb)
      	self.p.enqueue('setBitmap',(self.mediaNodeName, bitmap))
        self.p.enqueue('resize',(self.mediaNodeName, self.width, self.height,'centre','centre'))

    def run(self):
        self.p.enqueue('setOpacity',(self.mediaNodeName,1))
        self.p.enqueue('timer',(int(self.duration) * 1000,self.parent.next))
        self.startStats()

    def requiredFiles(self):
        return [str(self.options['uri'])]
	
    def dispose(self):
        self.p.enqueue('del',self.mediaNodeName)
        self.returnStats()
        self.parent.tNext()
