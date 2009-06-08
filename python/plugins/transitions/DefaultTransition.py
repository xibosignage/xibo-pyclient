#!/usr/bin/python
# -*- coding: utf-8 -*-

from XiboTransition import XiboTransition
from threading import Thread, Semaphore

class DefaultTransition(XiboTransition):
    "Abstract Class - Interface for Transitions"

    def run(self):
	self.callback()
