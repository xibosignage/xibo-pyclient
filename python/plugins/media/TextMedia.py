#!/usr/bin/python
# -*- coding: utf-8 -*-

from XiboMedia import XiboMedia
from threading import Thread

class TextMedia(XiboMedia):
    def run(self):
	self.parent.next()
