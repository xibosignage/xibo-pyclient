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

class TvMedia(XiboMedia):
    def add(self):
        # TODO:
        # Must check here for existance of the v4l device. Adding a camera node with a non-existant v4l device causes a
        # crash which cannot be caught by the play loop exception handling.
        tmpXML = '<camera device="' + str(self.options['device']) + '" source="' + str(self.options['driver']) + '" id="' + self.mediaNodeName + '" capturewidth="640" captureheight="480" pixelformat="YUYV422" framerate="30" opacity="0" />'
        self.p.enqueue('add',(tmpXML,self.regionNodeName))
        self.p.enqueue('play', self.mediaNodeName)
        self.p.enqueue('resize',(self.mediaNodeName, self.width, self.height,'centre','centre'))

    def run(self):
        self.p.enqueue('setOpacity',(self.mediaNodeName,1))
        self.p.enqueue('timer',(int(self.duration) * 1000,self.parent.next))
        self.startStats()

    def dispose(self):
        self.returnStats()
        self.p.enqueue('del',self.mediaNodeName)
        self.parent.tNext()
