#!/usr/bin/python
# -*- coding: utf-8 -*-

from XiboMedia import XiboMedia
from threading import Thread

class VideoMedia(XiboMedia):
    def __init__(self,log):
	Thread.__init__(self)
	log.log(2,"info","VideoMedia loaded!")

    def run(self):
	pass
