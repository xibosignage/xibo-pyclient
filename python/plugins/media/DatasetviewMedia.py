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

from XiboMedia import XiboMedia
from threading import Thread
import shutil
import math
import os
import codecs

class DatasetviewMedia(XiboMedia):
    def add(self):
        self.tmpPath = os.path.join(self.libraryDir,self.mediaNodeName + "-tmp.html")
        tmpXML = '<browser id="' + self.mediaNodeName + '" opacity="0" width="' + str(self.width) + '" height="' + str(self.height) + \
                '" />'
        self.p.enqueue('add',(tmpXML,self.regionNodeName))

        # Check updateInterval is set.
        # Early releases of the server missed this so catch those.
        try:
            tmpUI = int(self.options['updateInterval'])
        except KeyError:
            self.options['updateInterval'] = 10

    def run(self):
        # Check if cached content is too old
        # Download new content if needed
        self.download()

        # Copy the cache to temp file
        try:
            shutil.copyfile(os.path.join(self.libraryDir,self.mediaId) + '-cache.xml',
                            self.tmpPath)
        except IOError:
            # Unable to copy file
            # Move on?!
            self.dispose()

        # Display content
        self.p.enqueue('browserNavigate',(self.mediaNodeName,"file://" + os.path.abspath(self.tmpPath),self.finishedRendering))
        self.p.enqueue('timer',(int(self.duration) * 1000,self.parent.next))
        self.startStats()

    def requiredFiles(self):
        return []
	
    def dispose(self):
        self.returnStats()
        self.p.enqueue('del',self.mediaNodeName)
        try:
            os.remove(self.tmpPath)
        except:
            self.log.log(0,"error","Unable to delete file %s" % (self.tmpPath))
        self.parent.tNext()
 
    def finishedRendering(self):
        bo = self.browserOptions()
        optionsTuple = (self.mediaNodeName,bo[0],bo[1])
        self.p.enqueue('browserOptions',optionsTuple)
                
        # Make the browser visible
        self.p.enqueue('setOpacity',(self.mediaNodeName,1))
    
    def browserOptions(self):
        scroll = False
        trans = True
              
        return (trans,scroll)

    def download(self):
        
        tries = 3
        i = 0
        flag = False
        
        # If libraryDir/self.mediaId-cache.xml exists then check if it's too old to use
        try:
    	    mtime = os.path.getmtime(os.path.join(self.libraryDir,self.mediaId + '-cache.xml'))
            if time.time() < (mtime + (int(self.options['updateInterval']) * 60)):
                return
        except:
            # File probably doesn't exist. Do nothing.
            pass
        
        while i < tries and flag == False:
            try:
                # print "******* Passing in L:%s R:%s M:%s" % (self.parent.parent.l.layoutID,self.parent.regionId,self.mediaId)
                s = self.parent.parent.parent.xmds.GetResource(self.parent.parent.l.layoutID,self.parent.regionId,self.mediaId)
                flag = True
            except:
                self.log.log(1,"error",_("Unable to load Resource from XMDS."))
            i += 1
        
        if flag:
            try:
                try:
                    f = open(os.path.join(self.libraryDir,self.mediaId) + '-cache.xml','w')
                    f.write(s.encode("utf-8"))
                finally:
                    f.close()
            except:
                self.log.log(0,"error",_("Unable to write %s") % os.path.join(self.libraryDir,self.mediaId) + '-cache.xml')     
