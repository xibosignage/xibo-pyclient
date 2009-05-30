#!/usr/bin/python
# -*- coding: utf-8 -*-

from threading import Thread

class XiboMedia(Thread):
    "Abstract Class - Interface for Media"
    def __init__(self,log): abstract
    def run(self): abstract
