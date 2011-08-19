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

from XiboTransition import XiboTransition
from threading import Thread, Semaphore

class CollapseTransition(XiboTransition):

    def run(self):
        self.lock = Semaphore()
        self.lock.acquire()

        # Only valid as an exit transition

        if self.media1 != None:
            if self.options1['transOutDuration'] > 0:
                self.outDuration = int(self.options1['transOutDuration'])
            else:
                self.outDuration = 1000

            self.__animate__(self.media1.getName(),self.media1.getX(), self.media1.getY(),self.media1.getWidth(),self.media1.getHeight(),self.outDuration,self.next)
            self.lock.acquire()

        self.callback()

    def next(self):
        self.lock.release()

    def __animate__(self,name,currentX,currentY,w,h,duration,callback):
        # ('ease', nodeName, animation duration, animation attribute, start position, finish position, callback on Stop, easeIn duration, easeOut duration)
        self.log.log(5,"info","CollapseTransition: Collapsing " + name + " over " + str(duration) + "ms")
        self.p.enqueue('anim',('linear',name,duration,'y',currentY,int(h/2),None))
        self.p.enqueue('anim',('linear',name,duration,'height',int(h),0,callback))
        self.p.enqueue('timer',(duration,self.next))

