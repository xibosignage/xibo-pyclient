#!/usr/bin/python
# -*- coding: utf-8 -*-

from XiboMedia import XiboMedia
from threading import Thread

class TextMedia(XiboMedia):
    def add(self):
        pass
    
    def run(self):
        self.parent.next()
    
    def dispose(self):
        self.parent.tNext()
