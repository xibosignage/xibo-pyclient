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
        
        # Semaphore to lock reading/updating the global posts array
        self.__lock = Semaphore()

        # Handles to the twitter and identica APIs
        self.twitter = None
        self.identica = None
        
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
        self.__posts = []
        
    def run(self):
        # Define costants to represent each service
        TWITTER = 0
        IDENTICA = 1
        
        # Pointer to the currently displayed post:
        self.__pointer = -1
        
        # Test data
        # TODO: Remove this whole section.
        self.__lock.acquire()
        self.__posts = [(IDENTICA,u'en', u'Welcome to #oggcamp', u'Thu, 01 April 2010 17:00:00 +0000', u'http://domain.com/image.jpg', '', u'alexharrington', 939002, None, None, 499900L)]
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
            tmpTwitter = self.updateTwitter()
            tmpIdentica = self.updateIdentica()
            
            # TODO: Deduplicate the posts we've pulled in from the Microblogs
            
            # Update self.__posts with the new content as required
            # Lock the semaphore as we write to __posts to avoid changing the array as the display thread reads it.
            self.__lock.acquire()
            # THIS IS WRONG!!
            for post in tmpTwitter:
                self.__posts.append(post)            
            self.__lock.release()
            
            # Sleep for suitable duration
            time.sleep(self.options['updateInterval'])
    
    def nextPost(self):
        tmpPost = ()
        # If the media has been disposed, do nothing.
        if not self.running:
            return
        
        # Take the next post from the posts array and display it
        
        # Move the pointer on one. If we hit the end then start back at 0
        self.__lock.acquire()
        if len(self.__posts) > 0:
            self.__pointer = (self.__pointer + 1) % len(self.__posts)
            tmpPost = self.__posts[self.__pointer]
        self.__lock.release()
        
        print tmpPost
        
        # Set a timer to force the post to change
        # TODO: Should the animation trigger this itself?
        self.p.enqueue('timer',(5 * 1000,self.nextPost))
        
    def dispose(self):
        self.running = False
        self.parent.tNext()
        
    def updateTwitter(self):
        # Pull new posts from Twitter and return new posts in a list
        
        # Define TWITTER
        TWITTER = 0

        # Find the highest number twitter post we have already
        # No need to lock the Semaphore as we're the only thread that will
        # be doing any writing.
        last_id = None
        for post in self.__posts:
            if post[0] == TWITTER and post[10] > last_id:
                last_id = post[10]
        
        # Call twitter API and get new matches
        if self.twitter == None:
            self.twitter = twython.core.setup()
        
        results = self.twitter.searchTwitter(self.options['term'], since_id=last_id)
        
        tmpTwitter = []
        for post in results["results"]:
            tmpTwitter.append((TWITTER,post['iso_language_code'],post['text'],post['created_at'],post['profile_image_url'],post['source'],post['from_user'],post['from_user_id'],post['to_user_id'],post['geo'],post['id']))
        
        return tmpTwitter
            
    def updateIdentica(self):
        pass
