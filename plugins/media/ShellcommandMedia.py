#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# Xibo - Digitial Signage - http://www.xibo.org.uk
# Copyright (C) 2012-2013 Alex Harrington
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
import subprocess
import urllib

class ShellcommandMedia(XiboMedia):
    def add(self):
        self.commandsEnabled = self.config.getboolean('ShellCommands', 'enabled')
        self.commandWhiteList = []

        self.options['linuxCommand'] = urllib.unquote_plus(str(self.options['linuxCommand']))

        if self.config.get('ShellCommands', 'whitelist') != '':
            self.commandWhiteList = self.config.get('ShellCommands', 'whitelist').split(',')

    def run(self):
        self.p.enqueue('timer',(1 * 1000,self.parent.next))
        self.startStats()

        if self.commandsEnabled:
            flag = True

            if self.commandWhiteList != []:
                flag = False

                for cmd in self.commandWhiteList:
                    if self.options['linuxCommand'].startswith(cmd):
                        flag = True
                        break

            if not flag:
                self.log.log(0,"error","Shellcommand not in command whitelist: %s" % self.options['linuxCommand']) 
                return

            try:
                subprocess.call(self.options['linuxCommand'], shell=True)
            except OSError:
                self.log.log(0,"error","Error executing command: %s" % self.options['linuxCommand']) 
        else:
            self.log.log(0,"error","Shell commands are disabled: %s" % self.options['linuxCommand']) 

    def dispose(self):
        self.returnStats()
        self.p.enqueue('del',self.mediaNodeName)
        self.parent.tNext()
