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

class FlyTransition(XiboTransition):

    def run(self):
        self.lock = Semaphore()
        self.lock.acquire()

        # TODO: Broken if exit and entrance transitions are both "fly".
        if not self.media1 is None:
            if self.options1['transOutDuration'] > 0:
                self.outDuration = int(self.options1['transOutDuration'])
            else:
                self.outDuration = 1000

            self.log.log(5,"info","Running FlyOut transition")
            self.__animate__(self.media1.getName(),self.media1.getX(),self.media1.getY(),self.media1.getWidth(),self.media1.getHeight(),self.options1["transOutDirection"],self.outDuration,self.next)
            self.lock.acquire()
    
        if not self.media2 is None:
            self.media2.start()

        if not self.media2 is None:
            if self.options2['transInDuration'] > 0:
                self.inDuration = int(self.options2['transInDuration'])
            else:
                self.inDuration = 1000

            self.__animate__(self.media2.getName(),0 - self.media2.getWidth(), 0 - self.media2.getHeight(),self.media2.getX(),self.media2.getY(),self.options2["transInDirection"],self.inDuration,self.next)
            self.lock.acquire()

        self.callback()

    def next(self):
        self.lock.release()

    def __animate__(self,name,currentX,currentY,w,h,direction,duration,callback):
        if direction == "N":
            self.p.enqueue('anim',('linear',name,duration,'y',currentY,(-10 -h),callback))
            return

        if direction == "NE":
            self.p.enqueue('anim',('linear',name,duration,'y',currentY,(-10 -h),None))
            self.p.enqueue('anim',('linear',name,duration,'x',currentX,(-10 -w),callback))
            return

        if direction == "E":
            self.p.enqueue('anim',('linear',name,duration,'x',currentX,(-10 -w),callback))
            return

        if direction == "SE":
            self.p.enqueue('anim',('linear',name,duration,'y',currentY,(10 + h),None))
            self.p.enqueue('anim',('linear',name,duration,'x',currentX,(-10 -w),callback))
            return

        if direction == "S":
            self.p.enqueue('anim',('linear',name,duration,'y',currentY,(10 + h),callback))
            return

        if direction == "SW":
            self.p.enqueue('anim',('linear',name,duration,'x',currentX,(10 + w),None))
            self.p.enqueue('anim',('linear',name,duration,'y',currentY,(10 + h),callback))
            return

        if direction == "W":
            self.p.enqueue('anim',('linear',name,duration,'x',currentX,(10 + w),callback))
            return

        if direction == "NW":
            self.p.enqueue('anim',('linear',name,duration,'x',currentX,(10 + w),None))
            self.p.enqueue('anim',('linear',name,duration,'y',currentY,(-10 -h),callback))
            return

