#!/usr/bin/python
# -*- coding: utf-8 -*-
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
