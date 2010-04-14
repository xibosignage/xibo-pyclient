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
import simplejson
import urllib2
import urllib
import cPickle

# Define costants to represent each service
TWITTER = 0
IDENTICA = 1

class MicroblogSearchMedia(XiboMedia):
    def add(self):
        self.running = True
        self.seq = 0
        self.tmpPath = os.path.join(self.libraryDir,self.mediaNodeName + "-tmp.html")
        
        self.opener =  urllib2.build_opener()
        
        # Semaphore to lock reading/updating the global posts array
        self.__lock = Semaphore()

        # Handles to the twitter and identica APIs
        # self.twitter = None
        # self.identica = None
        
        # Options that should come from the server
        # Added here for testing purposes
        self.options['length'] = 10
        self.options['twitter'] = bool("True")
        self.options['identica'] = bool("True")
        self.options['term'] = "#oggcamp"
        self.options['speed'] = 5
        self.options['fadeTime'] = 1
        
        # Create an empty array for the posts to sit in
        # Each element will be a dictionary in the following format:
        # {'xibo_src': 0, u'iso_language_code': u'en_GB', u'text': u"@bobobex @corenominal If you have an android device, give c:geo a look for !geocaching, or nudge me at oggcamp and I'll show you. 'sgood", u'created_at': u'Thu, 08 Apr 2010 08:03:38 +0000', u'profile_image_url': u'http://avatar.identi.ca/13737-48-20080711132350.png', u'to_user': None, u'source': u'web', u'from_user': u'jontheniceguy', u'from_user_id': u'13737', u'to_user_id': None, u'id': u'27725072'}
        
        self.__posts = []
        
    def run(self):
        # Start the region timer so the media dies at the right time.
        self.p.enqueue('timer',(int(self.duration) * 1000,self.timerElapsed))
        
        # Pointer to the currently displayed post:
        self.__pointer = -1
        
        # Open previous cache file (if exists) and begin playing out posts
        # Lock the semaphore as we write to __posts to avoid changing the array as the display thread reads it.
        try:
            try:
                self.__lock.acquire()
                self.__posts = cPickle.load(file(os.path.join(self.libraryDir,self.mediaId + ".pickled")))
            finally:
                self.__lock.release()
        except:
            # Load in some data to get us going
            self.__lock.acquire()
            self.__posts = [{'xibo_src': 1, u'iso_language_code': u'en_GB', u'text': u"Welcome to xibo Microblog Search Media", u'created_at': u'Thu, 08 Apr 2010 08:03:38 +0000', u'profile_image_url': u'http://avatar.identi.ca/1102-96-20081013131713.png', u'to_user': None, u'source': u'web', u'from_user': u'alexharrington', u'from_user_id': u'13737', u'to_user_id': None, u'id': u'27725072'}]
            self.__lock.release()

            self.log.log(4,"audit","Unable to read serialised representation of the posts array or this media has never run before.")
        
        self.nextPost()
                
        # Check that the updateInterval we've been given is sane
        try:
            self.options['updateInterval'] = int(self.options['updateInterval'])
        except:
            self.options['updateInterval'] = 5
        
        while self.running:
            self.log.log(0,"audit","%s: Waking up" % self.mediaId)
            try:
    	        mtime = os.path.getmtime(os.path.join(self.libraryDir,self.mediaId + '.pickled'))
            except:
                # File probably doesn't exist.
                # Pretend the file was last updated more than updateInterval ago
                self.log.log(0,"audit","%s: Post cache does not exist.")
                mtime = time.time() - (self.options['updateInterval'] * 60) - 10
            
            if time.time() > (mtime + (self.options['updateInterval'] * 60)):
                # Download new posts and add them to the rotation
                self.log.log(0,"audit","%s: Getting new posts from Microblogs" % self.mediaId)
                tmpTwitter = self.updateTwitter()
                tmpIdentica = self.updateIdentica()
                tmpPosts = []
                
                # Deduplicate the posts we've pulled in from Twitter against Identica and __posts
                for post in tmpTwitter:
                    inIdentica = False
                    inPosts = False
                    
                    # See if the post is in the tmpIdentica array
                    for cmpPost in tmpIdentica:
                        if post['text'] == cmpPost['text'] and post['from_user'] == cmpPost['from_user']:
                            inIdentica = True
                            
                    # See if the post is in the __posts array
                    for cmpPost in self.__posts:
                        if post['text'] == cmpPost['text'] and post['from_user'] == cmpPost['from_user']:
                            inPosts = True
                
                    # Update self.__posts with the new content as required
                    # Lock the semaphore as we write to __posts to avoid changing the array as the display thread reads it.
                    if inIdentica or inPosts:
                        # The post already exists or is in Identica too
                        # Ignore the twitter version
                        pass
                    else:
                        tmpPosts.append(post)
                
                # Deduplicate the posts we've pulled in from Identica against __posts
                # (They're already deduplicated against Twitter
                for post in tmpIdentica:
                    inPosts = False
                    
                    for cmpPost in self.__posts:
                        if post['text'] == cmpPost['text'] and post['from_user'] == cmpPost['from_user']:
                            inPosts = True
                    
                    if inPosts:
                        # The post already exists in __posts.
                        # Ignore the identica version
                        pass
                    else:
                        tmpPosts.append(post)    
                
                # Remove enough old posts to ensure we maintain at least self.options['length'] posts
                # but allow an overflow if there are more new posts than we can handle
                # Lock the __posts list while we work on it.
                self.log.log(0,"audit","%s: Got %s new posts" % (self.mediaId,len(tmpPosts)))
                self.__lock.acquire()
                
                if len(tmpPosts) >= self.options['length']:
                    # There are more new posts than length.
                    # Wipe the whole existing __posts array out
                    self.__posts = []
                else:
                    # If there are more items in __posts than we're allowed to show
                    # trim it down to max now
                    if len(self.__posts) > self.options['length']:
                        self.__posts = self.__posts[0:self.options['length'] - 1]
                    
                    # Now remove len(tmpPosts) items from __posts
                    self.__posts = self.__posts[0:(self.options['length'] - len(tmpPosts) - 1)]
                
                # Reverse the __posts array as we can't prepend to an array
                self.__posts.reverse()
                
                # Reverse the tmpPosts array so we get newest items first
                tmpPosts.reverse()
                
                # Finally add the new items to the list
                for post in tmpPosts:
                    self.__posts.append(post)
                
                # And finally switch the array back around again to compensate for reversing it earlier
                self.__posts.reverse()
                
                # Unlock the list now we've finished writing to it
                self.__lock.release()
                
                # Serialize self.__posts for next time
                try:
                    try:
                        self.__lock.acquire()
                        f = codecs.open(os.path.join(self.libraryDir,self.mediaId + ".pickled"),mode='w',encoding="utf-8")
                        cPickle.dump(self.__posts, f)
                    finally:
                        f.close()
                        self.__lock.release()
                except IOError:
                    self.log.log(0,"error","Unable to write serialised representation of the posts array")
                except:
                    self.log.log(0,"error","Unexpected exception trying to write serialised representation of the posts array")
            # End If (If we should update on this run
            else:
                self.log.log(0,"audit","%s: Posts are still fresh." % self.mediaId)
            
            self.log.log(0,"audit","%s: Sleeping 60 seconds" % self.mediaId)
            # Sleep for 1 minute
            time.sleep(60)
            
        # End While loop
        self.log.log(0,"audit","%s: Media has completed. Stopping updating." % self.mediaId)
    
    def nextPost(self):
        tmpPost = ()
        # If the media has been disposed, do nothing.
        if not self.running:
            return
        
        # Move the pointer on one. If we hit the end then start back at 0
        # Take the next post from the posts array and display it
        self.__lock.acquire()
        if len(self.__posts) > 0:
            self.__pointer = (self.__pointer + 1) % len(self.__posts)
            tmpPost = self.__posts[self.__pointer]
        self.__lock.release()
        
        # TODO: Get the template we get from the server and insert appropriate fields
        service = ''
        if tmpPost['xibo_src'] == TWITTER:
            service = "via Twitter"
        elif tmpPost['xibo_src'] == IDENTICA:
            service = "via Identica"
            
        tmpHtml = "<html><meta http-equiv=\"content-type\" content=\"text/html; charset=utf-8\"><body><blockquote><img width=\"100\" height=\"100\" src=\"%s\" align=\"left\"><font color=\"white\" face=\"Arial\" size=\"6\"><u><b>%s:</b></u><br>%s</font><br><font color=\"white\" face=\"Arial\" size=\"3\">%s</font></blockquote></body></html>" % (tmpPost['profile_image_url'], tmpPost['from_user'], tmpPost['text'], service)
        
        try:
            try:
                f = codecs.open(self.tmpPath,mode='w',encoding="utf-8")
                f.write(tmpHtml)
                tmpHtml = None
            finally:
                f.close()
        except:
            self.log.log(0,"error","Unable to write " + self.tmpPath)
            self.parent.next()
            return
        
        # Increment the unique identifier for the browsernodes - but within a sensible limit.
        if self.seq < 1000:
            self.seq += 1
        else:
            self.seq = 1
        tmpXML = '<browser id="' + self.mediaNodeName + '-' + str(self.seq) + '" opacity="0" width="' + str(self.width) + '" height="' + str(self.height) + '"/>'
        self.p.enqueue('add',(tmpXML,self.regionNodeName))
        self.p.enqueue('browserNavigate',(self.mediaNodeName + '-' + str(self.seq),"file://" + os.path.abspath(self.tmpPath),self.fadeIn))
    
    def fadeIn(self):
        # Once the next post has finished rendering, fade it in
        self.p.enqueue('browserOptions',(self.mediaNodeName + '-' + str(self.seq), True, False))
        self.p.enqueue('anim',('fadeIn',self.mediaNodeName + '-' + str(self.seq), self.options['fadeTime'] * 1000, None))
        
        # Set a timer to force the post to change
        self.p.enqueue('timer',((self.options['speed'] + self.options['fadeTime']) * 1000,self.fadeOut))
    
    def fadeOut(self):
        # After the current post times out it calls this function which fades out the current node and then starts the next node
        # fading in.
        self.p.enqueue('anim',('fadeOut',self.mediaNodeName + '-' + str(self.seq), self.options['fadeTime'] * 1000, self.nextPost))
        
    def dispose(self):
        # Remember that we've finished running
        self.running = False
        
        # Clean up any temporary files left
        try:
            os.remove(self.tmpPath)
        except:
            self.log.log(0,"error","Unable to delete file %s" % (self.tmpPath))
            
        self.parent.tNext()
    
    def timerElapsed(self):
        # TODO: This function should not be necessary.
        # As soon as dispose() is properly called this can be removed
        
        # Remember that we've finished running
        self.running = False
        
        # Clean up any temporary files left
        try:
            os.remove(self.tmpPath)
        except:
            self.log.log(0,"error","Unable to delete file %s" % (self.tmpPath))
        
        # Tell our parent we're finished
        self.parent.next()
        
    def updateTwitter(self):
        """ Pull new posts from Twitter and return new posts in a list """
        
        if not self.options['twitter']:
            return []
        
        # Find the highest number twitter post we have already
        # No need to lock the Semaphore as we're the only thread that will
        # be doing any writing.
        last_id = None
        for post in self.__posts:
            if post['xibo_src'] == TWITTER and long(post['id']) > last_id:
                last_id = long(post['id'])
        
        # Call twitter API and get new matches

        results = self.searchMicroblog("http://search.twitter.com/search.json", self.options['term'], since_id=last_id)
        
        tmpTwitter = []
        for post in results["results"]:
            post['xibo_src'] = TWITTER
            tmpTwitter.append(post)
        
        return tmpTwitter
            
    def updateIdentica(self):
        """ Pull new posts from Identi.ca and return new posts in a list """

        if not self.options['identica']:
            return []
        
        # Find the highest number identi.ca post we have already
        # No need to lock the Semaphore as we're the only thread that will
        # be doing any writing.
        last_id = None
        for post in self.__posts:
            if post['xibo_src'] == IDENTICA and long(post['id']) > last_id:
                last_id = long(post['id'])
        
        # Call identica API and get new matches
        
        results = self.searchMicroblog("http://identi.ca/api/search.json", self.options['term'], since_id=last_id)
        
        tmpIdentica = []
        for post in results["results"]:
            post['xibo_src'] = IDENTICA
            tmpIdentica.append(post)
        
        return tmpIdentica
    
    # This method taken from Twython as it does not support connecting to identi.ca yet
    def constructApiURL(self, base_url, params):
        return base_url + "?" + "&".join(["%s=%s" %(key, value) for (key, value) in params.iteritems()])
    
    # This method taken from Twython as it does not support connecting to identi.ca yet
    # Modified from "searchTwitter" to take an api_base to allow switching between services.
    def searchMicroblog(self, api_base, search_query, **kwargs):
        """searchTwitter(search_query, **kwargs)

        Returns tweets that match a specified query.

        Parameters:
        callback - Optional. Only available for JSON format. If supplied, the response will use the JSONP format with a callback of the given name.
        lang - Optional. Restricts tweets to the given language, given by an ISO 639-1 code.
        locale - Optional. Language of the query you're sending (only ja is currently effective). Intended for language-specific clients; default should work in most cases.
        rpp - Optional. The number of tweets to return per page, up to a max of 100.
        page - Optional. The page number (starting at 1) to return, up to a max of roughly 1500 results (based on rpp * page. Note: there are pagination limits.)
        since_id - Optional. Returns tweets with status ids greater than the given id.
        geocode - Optional. Returns tweets by users located within a given radius of the given latitude/longitude, where the user's location is taken from their Twitter profile. The parameter value is specified by "latitide,longitude,radius", where radius units must be specified as either "mi" (miles) or "km" (kilometers). Note that you cannot use the near operator via the API to geocode arbitrary locations; however you can use this geocode parameter to search near geocodes directly.
        show_user - Optional. When true, prepends "<user>:" to the beginning of the tweet. This is useful for readers that do not display Atom's author field. The default is false.

        Usage Notes:
        Queries are limited 140 URL encoded characters.
        Some users may be absent from search results.
        The since_id parameter will be removed from the next_page element as it is not supported for pagination. If since_id is removed a warning will be added to alert you.
        This method will return an HTTP 404 error if since_id is used and is too old to be in the search index.
        Applications must have a meaningful and unique User Agent when using this method.
        An HTTP Referrer is expected but not required. Search traffic that does not include a User Agent will be rate limited to fewer API calls per hour than
        applications including a User Agent string. You can set your custom UA headers by passing it as a respective argument to the setup() method.
        """

        searchURL = self.constructApiURL(api_base, kwargs) + "&" + urllib.urlencode({"q": self.unicode2utf8(search_query)})

        try:
            return simplejson.load(self.opener.open(searchURL))
        except HTTPError, e:
            raise TwythonError("getSearchTimeline() failed with a %s error code." % `e.code`, e.code)
    
    # This method taken from twython
    def unicode2utf8(self, text):
        try:
            if isinstance(text, unicode):
                text = text.encode('utf-8')
        except:
            pass
        
        return text
