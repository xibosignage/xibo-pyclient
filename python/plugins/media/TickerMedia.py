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

from XiboMedia import XiboMedia
from threading import Thread
import FeedParser.feedparser

class TickerMedia(XiboMedia):
    def run(self):
	# TODO: Remove this return
	self.parent.next()
	return
	# Insert a cacheTimeout field to options.
	# This should become part of the XLF in the future.
	self.options['cacheTimeout'] = 20
	self.feed = None

	# If data/self.mediaId-cache.xml exists then check if it's too old to use
	if os.path.exists('data' + os.sep + self.mediaId + '-cache.xml'):
		file_stats = os.stat('data' + os.sep + self.mediaId + '-cache.xml')
		mtime = file_stats[stat.ST_MTIME]
		if time.ctime() > (mtime + (self.options['cacheTimeout'] * 60)):
			self.feed = Feedparser.feedparser.parse('data' + os.sep + self.mediaId + '-cache.xml')
		else:
			self.feed = Feedparser.feedparser.parse(self.options['uri'])
	else:
		self.feed = Feedparser.feedparser.parse(self.options['uri'])

	self.log.log(3,"info","Feed title: " + self.feed['feed']['title'])

	# TODO: Broken :( - Need to figure out the import properly.
