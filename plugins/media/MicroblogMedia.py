#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# Xibo - Digitial Signage - http://www.xibo.org.uk
# Copyright (C) 2010-11 Alex Harrington
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
import inspect

# Define costants to represent each service
TWITTER = 0
IDENTICA = 1

class MicroblogMedia(XiboMedia):
    def add(self):
        self.running = True
        self.tmpPath = os.path.join(self.libraryDir,self.mediaNodeName + "-tmp.html")
        
        self.opener =  urllib2.build_opener()
        
        # Semaphore to lock reading/updating the global posts array
        self.__lock = Semaphore()
        
        # Options:
        # <searchTerm>oggcamp</searchTerm><fadeInterval>1</fadeInterval><speedInterval>5</speedInterval><updateInterval>10</updateInterval><historySize>15</historySize><twitter>1</twitter><identica>1</identica></options>

        self.options['historySize'] = int(self.options['historySize'])
        self.options['twitter'] = bool(int(self.options['twitter']))
        self.options['identica'] = bool(int(self.options['identica']))
        self.options['speedInterval'] = int(self.options['speedInterval'])
        self.options['fadeInterval'] = int(self.options['fadeInterval'])
        
        # Create an empty array for the posts to sit in
        # Each element will be a dictionary in the following format:
        # {'xibo_src': 0, u'iso_language_code': u'en_GB', u'text': u"@bobobex @corenominal If you have an android device, give c:geo a look for !geocaching, or nudge me at oggcamp and I'll show you. 'sgood", u'created_at': u'Thu, 08 Apr 2010 08:03:38 +0000', u'profile_image_url': u'http://avatar.identi.ca/13737-48-20080711132350.png', u'to_user': None, u'source': u'web', u'from_user': u'jontheniceguy', u'from_user_id': u'13737', u'to_user_id': None, u'id': u'27725072'}        
        self.__posts = []
        
        # Parse out the template element from the raw tag.
        try:
            for t in self.rawNode.getElementsByTagName('template'):
                self.templateNode = t
        
            for node in self.templateNode.childNodes:
                if node.nodeType == node.CDATA_SECTION_NODE:
                    self.template = node.data.encode('UTF-8')
                    self.log.log(5,'audit','Template is: ' + self.template)
        except:
            self.log.log(2,'error','%s Error parsing out the template from the xlf' % self.mediaNodeName)
            self.template = ""

        # Parse out the nocontent element from the raw tag
        try:
            for t in self.rawNode.getElementsByTagName('nocontent'):
                self.nocontentNode = t
        
            for node in self.nocontentNode.childNodes:
                if node.nodeType == node.CDATA_SECTION_NODE:
                    self.nocontent = node.data.encode('UTF-8')
                    self.log.log(5,'audit','No Content is: ' + self.nocontent)
        except:
            self.log.log(2,'error','%s Error parsing out the nocontent from the xlf' % self.mediaNodeName)
            self.nocontent = ""
        
    def run(self):
        # Kickoff the display output thread
        self.displayThread = MicroblogMediaDisplayThread(self.log,self.p,self)
        self.displayThread.start()
    
        # Start the region timer so the media dies at the right time.
        self.p.enqueue('timer',(int(self.duration) * 1000,self.timerElapsed))
        
        tmpXML = '<browser id="' + self.mediaNodeName + '" opacity="0" width="' + str(self.width) + '" height="' + str(self.height) + '"/>'
        self.p.enqueue('add',(tmpXML,self.regionNodeName))

        self.startStats()
        
        # Pointer to the currently displayed post:
        self.__pointer = -1
        
        # Open previous cache file (if exists) and begin playing out posts
        # Lock the semaphore as we write to __posts to avoid changing the array as the display thread reads it.
        try:
            try:
                self.log.log(9,'info','%s acquiring lock to read pickled file.' % self.mediaId)
                self.__lock.acquire()
                self.log.log(9,'info','%s acquired lock to read pickled file.' % self.mediaId)
                tmpFile = open(os.path.join(self.libraryDir,self.mediaId + ".pickled"), 'rb')
                self.__posts = cPickle.load(tmpFile)
                tmpFile.close()
            finally:
                self.__lock.release()
                self.log.log(9,'info','%s releasing lock after reading pickled file.' % self.mediaId)
        except:
            # Erase any pickle file that may be existing but corrupted  
            try:
                os.remove(os.path.join(self.libraryDir,self.mediaId + ".pickled"))
                self.log.log(9,'info','%s erasing corrupt pickled file.' % self.mediaId)
            except:
                self.log.log(9,'info','%s unable to erase corrupt pickled file.' % self.mediaId)

            self.log.log(5,"audit","Unable to read serialised representation of the posts array or this media has never run before.")
            self.__lock.release()
        
        self.displayThread.nextPost()
                
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
                
                # Remove enough old posts to ensure we maintain at least self.options['historySize'] posts
                # but allow an overflow if there are more new posts than we can handle
                # Lock the __posts list while we work on it.
                self.log.log(0,"audit","%s: Got %s new posts" % (self.mediaId,len(tmpPosts)))
                self.log.log(9,'info','%s acquiring lock to process posts.' % self.mediaId)
                self.__lock.acquire()
                self.log.log(9,'info','%s acquired lock to process posts.' % self.mediaId)
                
                if len(tmpPosts) >= self.options['historySize']:
                    # There are more new posts than length.
                    # Wipe the whole existing __posts array out
                    self.__posts = []
                else:
                    # If there are more items in __posts than we're allowed to show
                    # trim it down to max now
                    if len(self.__posts) > self.options['historySize']:
                        self.__posts = self.__posts[0:self.options['historySize'] - 1]
                    
                    # Now remove len(tmpPosts) items from __posts
                    self.__posts = self.__posts[0:(self.options['historySize'] - len(tmpPosts) - 1)]
                
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
                self.log.log(9,'info','%s releasing lock after processing posts.' % self.mediaId)
                
                # Serialize self.__posts for next time
                try:
                    try:
                        self.log.log(9,'info','%s acquiring lock to write pickled file.' % self.mediaId)
                        self.__lock.acquire()
                        self.log.log(9,'info','%s acquired lock to write pickled file.' % self.mediaId)
                        f = open(os.path.join(self.libraryDir,self.mediaId + ".pickled"),mode='wb')
                        cPickle.dump(self.__posts, f, True)
                    finally:
                        f.close()
                        self.__lock.release()
                        self.log.log(9,'info','%s releasing lock to write pickled file.' % self.mediaId)
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
        self.__lock.release()
    
    def dispose(self):
        # Remember that we've finished running
        self.displayThread.dispose()
        self.running = False
        self.__lock.release()
        self.p.enqueue('del', self.mediaNodeName)
        
        self.returnStats()
        
        # Clean up any temporary files left
        try:
            os.remove(self.tmpPath)
        except:
            self.log.log(0,"error","Unable to delete file %s" % (self.tmpPath))
            
        self.parent.tNext()
        
    def getLock(self):
        self.__lock.acquire()
        
    def releaseLock(self):
        self.__lock.release()
        
    def posts(self):
        return self.__posts
    
    def timerElapsed(self):
        # TODO: This function should not be necessary.
        # As soon as dispose() is properly called this can be removed
        
        # Remember that we've finished running
        self.running = False
        self.__lock.release()
        self.returnStats()
        self.displayThread.dispose()
        
        self.p.enqueue('del', self.mediaNodeName)
        
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

        try:
            results = self.searchMicroblog("http://search.twitter.com/search.json", self.options['searchTerm'], since_id=last_id)
        except:
            results = []
        
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

        try:        
            results = self.searchMicroblog("http://identi.ca/api/search.json", self.options['searchTerm'], since_id=last_id)
        except:
            results = []
        
        tmpIdentica = []
        for post in results["results"]:
            post['xibo_src'] = IDENTICA
            tmpIdentica.append(post)
        
        return tmpIdentica
    
    # This method taken from Twython as it does not support connecting to identi.ca yet
    # The MIT License
    #
    # Copyright (c) 2009 Ryan McGrath
    #
    # Permission is hereby granted, free of charge, to any person obtaining a copy
    # of this software and associated documentation files (the "Software"), to deal
    # in the Software without restriction, including without limitation the rights
    # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    # copies of the Software, and to permit persons to whom the Software is
    # furnished to do so, subject to the following conditions:
    #
    # The above copyright notice and this permission notice shall be included in
    # all copies or substantial portions of the Software.
    #
    # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    # THE SOFTWARE.
    def constructApiURL(self, base_url, params):
        return base_url + "?" + "&".join(["%s=%s" %(key, value) for (key, value) in params.iteritems()])
    
    # This method taken from Twython as it does not support connecting to identi.ca yet
    # Modified from "searchTwitter" to take an api_base to allow switching between services.
    # The MIT License
    #
    # Copyright (c) 2009 Ryan McGrath
    # Portions (c) 2010 Alex Harrington
    #
    # Permission is hereby granted, free of charge, to any person obtaining a copy
    # of this software and associated documentation files (the "Software"), to deal
    # in the Software without restriction, including without limitation the rights
    # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    # copies of the Software, and to permit persons to whom the Software is
    # furnished to do so, subject to the following conditions:
    #
    # The above copyright notice and this permission notice shall be included in
    # all copies or substantial portions of the Software.
    #
    # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    # THE SOFTWARE.

    def searchMicroblog(self, api_base, search_query, **kwargs):
        """searchMicroblog(search_query, **kwargs)

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

        return simplejson.load(self.opener.open(searchURL))
    
    # This method taken from twython
    # The MIT License
    #
    # Copyright (c) 2009 Ryan McGrath
    #
    # Permission is hereby granted, free of charge, to any person obtaining a copy
    # of this software and associated documentation files (the "Software"), to deal
    # in the Software without restriction, including without limitation the rights
    # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    # copies of the Software, and to permit persons to whom the Software is
    # furnished to do so, subject to the following conditions:
    #
    # The above copyright notice and this permission notice shall be included in
    # all copies or substantial portions of the Software.
    #
    # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    # THE SOFTWARE.

    def unicode2utf8(self, text):
        try:
            if isinstance(text, unicode):
                text = text.encode('utf-8')
        except:
            pass
        
        return text

class MicroblogMediaDisplayThread(Thread):
    def __init__(self,log,player,parent):
        Thread.__init__(self)
        self.parent = parent
        self.p = player
        self.log = log
        self.__lock = Semaphore()
        self.__running = True
        self.__pointer = 0
        
    def run(self):
        tmpPost = None

        while self.__running:
            self.__lock.acquire()
            self.log.log(9,'info', 'MicroblogMediaDisplayThread: Sleeping')
            self.__lock.acquire()
            self.log.log(9,'info', 'MicroblogMediaDisplayThread: Wake Up')
            if self.__running:
                # Do stuff
                self.parent.getLock()
                if len(self.parent.posts()) > 0:
                    self.__pointer = (self.__pointer + 1) % len(self.parent.posts())
                    tmpPost = self.parent.posts()[self.__pointer]
                self.parent.releaseLock()
                
                # Get the template we get from the server and insert appropriate fields
                # If there's no posts then show the no content template, otherwise show the content template
                if tmpPost == None:
                    # TODO: Get no content template
                    tmpHtml = self.parent.nocontent
                else:
                    service = ''
                    if tmpPost['xibo_src'] == TWITTER:
                        tmpPost['service'] = "Twitter"
                    elif tmpPost['xibo_src'] == IDENTICA:
                        tmpPost['service'] = "Identica"

                    tmpHtml = self.parent.template
                
                    # Replace [tag] values with data
                    for key, value in tmpPost.items():
                        tmpHtml = tmpHtml.replace("[%s]" % key, "%s" % value)

                try:
                    try:
                        f = codecs.open(self.parent.tmpPath,mode='w',encoding="utf-8")
                        f.write(tmpHtml)
                        tmpHtml = None
                    finally:
                        f.close()
                except:
                    self.log.log(0,"error","Unable to write " + self.parent.tmpPath)
                    self.parent.parent.next()
                    return

                # self.p.enqueue('del', self.parent.mediaNodeName)
                # tmpXML = '<browser id="' + self.parent.mediaNodeName + '" opacity="0" width="' + str(self.parent.width) + '" height="' + str(self.parent.height) + '"/>'
                # self.p.enqueue('add',(tmpXML,self.parent.regionNodeName))
                self.p.enqueue('browserNavigate',(self.parent.mediaNodeName,"file://" + os.path.abspath(self.parent.tmpPath),self.fadeIn))
                self.log.log(9,'info','MicroblogMediaDisplayThread: Finished Loop')
        
        self.log.log(9,'info', 'MicroblogMediaDisplayThread: Exit')
        self.__lock.release()
        
    def nextPost(self):
        # Release the lock so next can run
        self.log.log(9,'info', 'MicroblogMediaDisplayThread: nextPost called by ' + inspect.getframeinfo(inspect.currentframe().f_back)[2] + '.' + str(inspect.getframeinfo(inspect.currentframe().f_back)[1]))
        self.__lock.release()
        
    def dispose(self):
        self.__running = False
        self.__lock.release()
         
    def fadeIn(self):
        self.log.log(9,'info','Starting fadeIn')
        self.log.log(9,'info', 'MicroblogMediaDisplayThread: fadeIn called by ' + inspect.getframeinfo(inspect.currentframe().f_back)[2] + '.' + str(inspect.getframeinfo(inspect.currentframe().f_back)[1]))
        # Once the next post has finished rendering, fade it in
        self.p.enqueue('browserOptions',(self.parent.mediaNodeName, True, False))
        self.p.enqueue('anim',('fadeIn',self.parent.mediaNodeName, self.parent.options['fadeInterval'] * 1000, None))
        
        # Set a timer to force the post to change
        self.p.enqueue('timer',((self.parent.options['speedInterval'] + self.parent.options['fadeInterval']) * 1000,self.fadeOut))
        self.log.log(9,'info','Finished fadeIn')
    
    def fadeOut(self):
        self.log.log(9,'info','Starting fadeOut')
        self.log.log(9,'info', 'MicroblogMediaDisplayThread: fadeOut called by ' + inspect.getframeinfo(inspect.currentframe().f_back)[2] + '.' + str(inspect.getframeinfo(inspect.currentframe().f_back)[1]))
        # After the current post times out it calls this function which fades out the current node and then starts the next node
        # fading in.
        self.p.enqueue('anim',('fadeOut',self.parent.mediaNodeName, self.parent.options['fadeInterval'] * 1000, self.nextPost))
        self.log.log(9,'info','Finished fadeOut')
