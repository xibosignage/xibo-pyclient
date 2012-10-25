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

from threading import Thread

class XiboTransition(Thread):
    "Abstract Class - Interface for Transitions"
    def __init__(self,log,player,media1,media2,callback,options1=None,options2=None):
	Thread.__init__(self)
	log.log(2,"info",self.__class__.__name__ + " plugin loaded!")
	self.log = log
	self.p = player
	self.media1 = media1
	self.media2 = media2
	self.callback = callback
	self.options1 = options1
	self.options2 = options2

	# Set an options1 and options2 dictionary
	if self.options1 == None:
		try:
			self.options1 = self.media1.options
		except:
			self.options1 = None
	if self.options2 == None:
		try:
			self.options2 = self.media2.options
		except:
			self.options2 = None

    def run(self):
        callback()
