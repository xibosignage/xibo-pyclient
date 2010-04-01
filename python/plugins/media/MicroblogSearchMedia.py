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
from threading import Thread, Semaphore
import sys, os, time, codecs
import twython

class MicroblogSearchMedia(XiboMedia):
    def add(self):
        self.running = True
        self.__lock = Semaphore()
        
        # Options that should come from the server
        # Added here for testing purposes
        self.options['length'] = 10
        self.options['twitter'] = bool("True")
        self.options['identica'] = bool("True")
        self.options['term'] = "#oggcamp"
        
        # TODO: Add a container to hold the posts
        
        
        # Create an empty array for the posts to sit in
        # Each element will be a tuple in the following format:
        #    (service, iso_language_code, text, created_at, profile_image_url, source, from_user, from_user_id, to_user_id, geo, id)
        # eg (IDENTICA, u"en", u"Welcome to #oggcamp", u"Thu, 01 April 2010 17:00:00 +0000", u"http://domain.com/image.jpg", u"&lt;a href=&quot;http://www.twitter.com/web&quot;&gt;web&lt;/a&gt;", u"alexharrington", 9494929, None, None, 392000100011L)
        self.__posts = {}
        
    def run(self):
        # Define costants to represent each service
        TWITTER = 0
        IDENTICA = 1
        
        # Pointer to the currently displayed post:
        self.__pointer = -1
        
        # Test data
        # TODO: Remove this whole section.
        self.__lock.acquire()
        self.__posts = {(IDENTICA,u'en', u'Welcome to #oggcamp', u'Thu, 01 April 2010 17:00:00 +0000', u'http://domain.com/image.jpg', '', u'alexharrington', 939002, None, None, 499900L)}
        self.__lock.release()

        # TODO: Open previous cache file (if exists) and begin playing out posts
        # Lock the semaphore as we write to __posts to avoid changing the array as the display thread reads it.
        self.nextPost()
                
        # Check that the updateInterval we've been given is sane
        try:
            self.options['updateInterval'] = int(self.options['updateInterval'])
        except:
            self.options['updateInterval'] = 60
        
        while self.running:
            # TODO: Download new posts and add them to the rotation
            
            
            # Update self.__posts with the new content as required
            # Lock the semaphore as we write to __posts to avoid changing the array as the display thread reads it.
            self.__lock.acquire()
            
            self.__lock.release()
            
            # Sleep for suitable duration
            time.sleep(self.options['updateInterval'])
    
    def nextPost(self):
        # Take the next post from the posts array and display it
        
        # Move the pointer on one. If we hit the end then start back at 0
        self.__lock.acquire()
        self.__pointer = (self.__pointer + 1) % len(self.__posts)
        tmpPost = self.__posts[self.__pointer]
        self.__lock.release()
        
        # Set a timer to force the post to change
        
    def dispose(self):
        self.running = False
        self.parent.tNext()
