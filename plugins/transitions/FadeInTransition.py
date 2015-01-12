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

class FadeInTransition(XiboTransition):
    "Abstract Class - Interface for Transitions"

    def run(self):
        self.lock = Semaphore()
        self.lock.acquire()

        if not self.media1 is None:
            if self.options1['transOutDuration'] > 0:
                self.outDuration = int(self.options1['transOutDuration'])
            else:
                self.outDuration = 1000

            self.p.enqueue('setOpacity',(self.media1.getName(),0.0))
            self.p.enqueue('anim',('fadeIn',self.media1.getName(),self.outDuration,self.next))
            self.lock.acquire()

        if not self.media2 is None:
            self.media2.start()

        if not self.media2 is None:
            if self.options2['transInDuration'] > 0:
                self.inDuration = int(self.options2['transInDuration'])
            else:
                self.inDuration = 1000

            self.p.enqueue('setOpacity',(self.media2.getName(),0.0))
            self.p.enqueue('anim',('fadeIn',self.media2.getName(),self.inDuration,self.next))
            self.lock.acquire()

        self.callback()		

    def next(self):
        self.lock.release()
