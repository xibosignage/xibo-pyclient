#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# Xibo - Digitial Signage - http://www.xibo.org.uk
# Copyright (C) 2009-2014 Alex Harrington
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
from GetResourceBase import GetResourceBase
from threading import Thread

class TextMedia(GetResourceBase):
    def cacheIsExpired(self):
        # Check if the file we have downloaded (if it exists) is newer than the last
        # layout modification date
        layout = self.parent.parent.l
        
        if layout.builtWithNoXLF:
            return False
        
        try:
    	    mtime = os.path.getmtime(os.path.join(self.libraryDir, self.mediaId + '-cache.xml'))
            if mtime > layout.getMtime():
                return False
        except:
            # File probably doesn't exist.
            # Fall through to the default
            pass
        
        return True

