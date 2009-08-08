#!/usr/bin/python
# -*- coding: utf-8 -*-

from threading import Thread

class XiboMedia(Thread):
    "Abstract Class - Interface for Media"

    def __init__(self,log,parent,player,mediaNode):
        """
        Represents a media item. Can be constructed with valid parent (RegionManager) and Player objects - by a real running layout
        or with None types when the Layout object is interegated to find out if all the media nodes are in a state ready to run.
        """
        Thread.__init__(self)
        self.__setupMedia__(log,parent,player,mediaNode)

    def requiredFiles(self):
        return []

    def add(self):
        pass

    def __setupMedia__(self,log,parent,player,mediaNode):
        log.log(2,"info",self.__class__.__name__ + " plugin loaded!")
        self.log = log
        self.parent = parent
        self.p = player
        self.mediaNode = mediaNode
        self.mediaNodeName = None
        self.mediaType = None
        self.duration = None
        self.schemaVersion = None
        self.invalid = False
        self.options = {}
        self.rawNode = None
        self.optionsNode = None

        if self.p == None:
            self.regionNodeName = 'null'
            self.regionNodeNameExt = 'null'
            self.width = '10'
            self.height = '10'
            self.mediaNodeNameExt = '-null'
        else:
            self.regionNodeName = self.parent.regionNodeName
            self.regionNodeNameExt = self.parent.regionNodeNameExt
            self.width = self.parent.width
            self.height = self.parent.height
            self.mediaNodeNameExt = "-" + str(self.p.nextUniqueId())

        # Calculate the media ID name
        try:
            self.mediaId = str(self.mediaNode.attributes['id'].value)
            self.mediaNodeName = "M" + self.mediaId + self.regionNodeNameExt + self.mediaNodeNameExt
        except KeyError:
            log.log(1,"error",_("Media XLF is invalid. Missing required id attribute"))
            self.mediaNodeName = "M-invalid-" + self.regionNodeNameExt + self.mediaNodeNameExt
            self.invalid = True
            return

        # Calculate the media type
        try:
            self.mediaType = str(self.mediaNode.attributes['type'].value)
        except KeyError:
            log.log(1,"error",_("Media XLF is invalid. Missing required type attribute"))
            self.invalid = True
            return

        # Calculate the media duration
        try:
            self.duration = str(self.mediaNode.attributes['duration'].value)
        except KeyError:
            log.log(1,"error",_("Media XLF is invalid. Missing required duration attribute"))
            self.invalid = True
            return

        # Find the options and raw nodes and assign them to self.rawNode and self.optionsNode
        for cn in self.mediaNode.childNodes:
            if cn.nodeType == cn.ELEMENT_NODE and cn.localName == "options":
                self.optionsNode = cn
            if cn.nodeType == cn.ELEMENT_NODE and cn.localName == "raw":
                self.rawNode = cn

        # Parse the options block in to the self.options[] array:
        for cn in self.optionsNode.childNodes:
            if cn.localName != None:
                self.options[str(cn.localName)] = cn.childNodes[0].nodeValue
                log.log(5,"info","Media Options: " + str(cn.localName) + " -> " + str(cn.childNodes[0].nodeValue))

    def run(self):
        # If there was a problem initialising the media object, kill it off and go to the next media item
        if self.invalid == True:
            self.parent.next()
            return

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height

    def getX(self):
        return 0

    def getY(self):
        return 0

    def getName(self):
        return self.mediaNodeName

    def requiredFiles(self):
        return []

    def dispose(self):
        # Media should dispose itself
        # Call tNext to release the regionManager lock.
        self.parent.tNext()

