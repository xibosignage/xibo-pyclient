#!/usr/bin/python

# -*- coding: utf-8 -*-

#
# Xibo - Digitial Signage - http://www.xibo.org.uk
# Copyright (C) 2011 Matt Holder
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

gettextAvailable = None

try:
	import gettext
	gettextAvailable = True
except:
	print "Could not import gettext"
	print "Creating dummy function for _()"
	def _(string):
		return string
try:
	import sys
except:
	print "Could not import sys module"
	sys.exit()

try:
	import uuid
except:
	print "Could not import uuid module"
	sys.exit()

try:
	import ConfigParser
except:
	print "Could not import ConfigParser module"
	sys.exit()

try:
	import os
except:
	print "Could not import os module"
	sys.exit()

try:
	import logging
except:
	print "Could not import logging module"
	sys.exit()

try:
	import pygtk
	pygtk.require("2.0")
except:
	print "Could not import pygtk"
	sys.exit()

try:
	import gtk
except:
	print "Could not import gtk"
	sys.exit(1)

try:
	import gtk.glade
except:
	print "Could not import gtk.glade"
	sys.exit(1)
	
try:
	import gobject
except:
	print "Could not import gobject"
	sys.exit()

#Only run this if gettext is available
if gettextAvailable:
	gettext.install('ivcm', './locale', unicode=False)


class xiboConfWindow:
	"""This is the PyWine application"""


	def __init__(self,clientConfFile,lift = False):

		#This is the location of the config. file for the client
		#itself. This comes from when the instance of the class
		#is created.
		self.clientConfFile = clientConfFile

		#Firstly, read in the values relating to log from the config. client config. file
		config = None
		try:
			config = ConfigParser.ConfigParser()
			config.read(self.clientConfFile)
		except:
			print "Could not open %s"%self.clientConfFile

		#Xibo client configuration file name
		logFileName="error.log"
		try:
			logFileName = config.get('Main','logFileName')
		except:
			pass

		logWriter="xiboLogScreen"
		try:
			logWriter = config.get('Main','logWriter')
		except:
			pass


		logLevel="INFO"
		try:
			logLevel = config.get('Main','logLevel')
		except:
			pass
		a=logging

		loggingLevel = None
		if logLevel == "INFO":
			loggingLevel = a.INFO
		elif logLevel == "WARNING":
			loggingLevel = a.WARNING
		elif logLevel == "ERROR":
			loggingLevel = a.ERROR
		
		if logWriter == "xiboLogScreen":
			a.basicConfig(level=loggingLevel)
		elif logWriter == "xiboLogFile":
			
			a.basicConfig(level=loggingLevel,filename=logFileName,filemode="w")

#		#Set up the logger
#		logging.basicConfig(level=logging.INFO,filename="error.log",filemode="w")
#		#format='%(asctime)s %(levelname)s %(lineno)d %(message)s'

		
		self.logger = a.getLogger("PyClientConfig")
		self.logger1 = a.getLogger("PyClientConfig.GUI")
		self.logger2 = a.getLogger('PyClientConfig.readConfig')
		self.logger3 = a.getLogger("PyClientConfig.saveConfigSignal")
		self.logger4 = a.getLogger("PyClientConfig.genClientID")
		self.logger5 = a.getLogger("PyClientConfig.getConfValues")
		self.logger6 = a.getLogger("PyClientConfig.advancedOptionsCheck")
		self.logger7 = a.getLogger("PyClientConfig.readConfigAppConf")
		self.logger8 = a.getLogger("PyClientConfig.offlineOperationToggle")
		self.logger9 = a.getLogger("PyClientConfig.clearFormSignal")
		self.logger10 = a.getLogger("PyClientConfig.onDestroy")
		self.logger11 = a.getLogger("PyClientConfig.saveSignal")
		self.logger12 = a.getLogger("PyclientConfig.LoadDefaultValues")

		self.logger1.info('Config. client config. file: %s'%self.clientConfFile)

		self.logger1.info("logWriter: %s"%logWriter)
		self.logger1.info("logLevel: %s"%logLevel)
		self.logger.info("logFileName: %s"%logFileName)
		
		#Name of the default log file for the python client
		self.pyClientLogName = "run.log"		


		#Read out the values from the client configuration file
		configValues = self.readConfigAppConf()

		#Take the options for log type from the file, and set the
		#class instance variable. The combo box is then populated from this.
		self.logWriterTypes = configValues["logTypeOptions"]		

		self.logger1.info("logWriter: %s"%self.logWriterTypes)

		#Take the options for the human readable log type options
		self.logWriterHumanTypes = configValues["logTypeHumanOptions"]

		self.logger1.info("logWriteHumanOptions: %s"%self.logWriterHumanTypes)

		#Take the location of the configuration file and set the class
		#instance variable. This path is then used when the config.
		#file is written		

		self.pyClientConfName = configValues["xiboClientConf"]
			
			
		self.logger1.info("Xibo client config. file: %s"%self.pyClientConfName)

		self.pyClientConfDefaultsName = "defaults.cfg"

		#Grab the directory location and check this directory exists.

		self.pyclientConfPath = configValues["clientConfLoc"]
		
		self.logger1.info("Xibo client config. file path: %s"%self.pyclientConfPath)
		
		self.logger1.info("Config file combined path: %s"%os.path.join(self.pyclientConfPath,self.pyClientConfName))
		
		#Take the options for scheduler type and add them to a class
		#instance variable

		self.schedulerOptions = configValues["schedulerOptions"]
		
		#Add a blank entry to the combo box, so that a blank option
		#can mean that the value is not written to the config. file
		self.schedulerOptions.insert(0,"")

		#Downloader options
		self.downloaderOptions = configValues["downloaderOptions"]
		self.downloaderOptions.insert(0,"")

		#Colour Depth options
		self.colourDepthOptions = configValues["colourDepthOptions"]
		self.colourDepthOptions.insert(0,"")

		#Lift enable options
		self.liftEnableOptions = ["True","False"]

		#Manual update options
		self.manualUpdateOptions = ["True","False"]

		#Set the Glade file
		self.builder = gtk.Builder()
		self.builder.add_from_file("gui.glade")
		self.builder.connect_signals(self)

		#Create instances of the text fields, window etc
		self.window = self.builder.get_object("mainWindow")
		self.clearButton = self.builder.get_object("clearFields")
		self.saveButton = self.builder.get_object("saveConfig")
		
		self.serverURLText = self.builder.get_object("serverURLText")
		self.clientIDText = self.builder.get_object("clientIDText")
		self.serverKeyText = self.builder.get_object("serverKeyText")
		self.refreshText = self.builder.get_object("refreshText")
		self.serverConnBool = self.builder.get_object("serverConnection")
		self.fullScreenBool = self.builder.get_object("fullScreen")
		self.screenWidthText = self.builder.get_object("screenWidthText")
		self.screenHeightText = self.builder.get_object("screenHeightText")
		self.captureStatisticsBool = self.builder.get_object("captureStatistics")
		self.queueSizeText = self.builder.get_object("queueSizeText")
		self.logLevelSpin = self.builder.get_object("logLevelSpin")
		self.logTypeCombo = self.builder.get_object("logTypeCombo")
		self.clientNameText = self.builder.get_object("clientNameText")

		self.offlineCheckButton = self.builder.get_object("offlineCheckButton")

		#Advanced options widgets

		self.liftDefaultTagText = self.builder.get_object('liftDefaultTagText')
		self.lift7TagText = self.builder.get_object('lift7TagText')
		self.lift6TagText = self.builder.get_object('lift6TagText')
		self.lift5TagText = self.builder.get_object('lift5TagText')
		self.lift4TagText = self.builder.get_object('lift4TagText')
		self.lift3TagText = self.builder.get_object('lift3TagText')
		self.lift2TagText = self.builder.get_object('lift2TagText')
		self.lift1TagText = self.builder.get_object('lift1TagText')
		self.lift0TagText = self.builder.get_object('lift0TagText')
		self.firstSerialText = self.builder.get_object('firstSerialText')
		self.secondSerialText = self.builder.get_object('secondSerialText')
		self.liftTriggerValue = self.builder.get_object('liftTriggerValue')
		self.liftEnableCombo = self.builder.get_object('liftEnableCombo')
		self.dateFormatEntry = self.builder.get_object('dateFormatEntry')
		self.libraryEntry = self.builder.get_object('libraryEntry')
		self.socketTimeSpin = self.builder.get_object('socketTimeSpin')
		self.checksumCheckButton = self.builder.get_object('checksumCheckButton')
		self.lowTextureCheckButton = self.builder.get_object('lowTextureCheckButton')
		self.framesSpin = self.builder.get_object('framesSpin')
		self.vwidthSpin = self.builder.get_object('vwidthSpin')
		self.vheightSpin = self.builder.get_object('vheightSpin')
		self.vrotateSpin = self.builder.get_object('vrotateSpin')
		self.schedulerCombo = self.builder.get_object("schedulerCombo")
		self.downloaderCombo = self.builder.get_object("downloaderCombo")
		self.colourDepthCombo = self.builder.get_object("colourDepthCombo")
		self.notebook1 = self.builder.get_object("notebook1")

		self.lift8TagText = self.builder.get_object("lift8TagText")
		self.lift9TagText = self.builder.get_object("lift9TagText")
		self.lift10TagText = self.builder.get_object("lift10TagText")
		self.lift11TagText = self.builder.get_object("lift11TagText")
		self.lift12TagText = self.builder.get_object("lift12TagText")
		self.lift13TagText = self.builder.get_object("lift13TagText")
		self.lift14TagText = self.builder.get_object("lift14TagText")
		self.lift15TagText = self.builder.get_object("lift15TagText")

		self.thirdSerialText = self.builder.get_object("thirdSerialText")
		self.fourthSerialText = self.builder.get_object("fourthSerialText")

		self.mediaInventoryCombo = self.builder.get_object("mediaInventoryCombo")

		self.popUpSettingsFrame = self.builder.get_object("popUpSettingsFrame")

		self.colourSelectdialog1 = self.builder.get_object("colourSelectdialog1")

		self.scanCodeNextText = self.builder.get_object("scanCodeNextText")
		self.scanCodeResetText = self.builder.get_object("scanCodeResetText")
		self.counterMaxSpin = self.builder.get_object("counterMaxSpin")

		self.osdBackColourText = self.builder.get_object("osdBackColourText")
		self.osdBackOpacitySpin = self.builder.get_object("osdBackOpacitySpin")
		self.osdFontSizeSpin = self.builder.get_object("osdFontSizeSpin")
		self.osdFontColourText = self.builder.get_object("osdFontColourText")
		self.osdWidthSpin = self.builder.get_object("osdWidthSpin")
		self.osdTimeoutSpin = self.builder.get_object("osdTimeoutSpin")
		self.osdBackColourButton = self.builder.get_object("osdBackColourButton")
		self.osdFontColourButton = self.builder.get_object("osdFontColourButton")

		self.scanCodePrevText = self.builder.get_object("scanCodePrevText")

		self.errorDialog = self.builder.get_object("errorDialog")
		self.messageDialog = self.builder.get_object("infoDialog")

		self.statsCaptureLabel = self.builder.get_object("statsCaptureLabel")
		self.statsQueueSizeLabel = self.builder.get_object("statsQueueSizeLabel")

		#Grab the log file link button and make it invisible by default
		self.logFileLinkButton = self.builder.get_object("logFileLinkButton")
		self.logFileLinkButton.hide()

		self.statsFrame = self.builder.get_object("frame2")
		
		#We want to be able to hide the lift options if the command line flag
		#has not been passed. We can do this by grabbing the 5th (4th when
		#counting from zero) page, and using the hide method.

		self.liftTabVisible = lift
		print self.liftTabVisible

		if lift == False:
			liftPage = self.notebook1.get_nth_page(4)		
			liftPage.hide()
			self.logger1.info("Lift options hidden")
			
			#Hide the statistics options unless the lift
			#tab is being shown
			self.captureStatisticsBool.hide()
			self.queueSizeText.hide()
			self.statsCaptureLabel.hide()
			self.statsQueueSizeLabel.hide()
			self.statsFrame.hide()

		else:
			self.logger1.info("Lift options available")

		#Set a class instance variable for whether the advanced tab is shown or not
		self.advancedTabVisible = False

		#Now hide the tab for the advanced settings and counter settings
		advancedPage = self.notebook1.get_nth_page(3)		
		counterPage = self.notebook1.get_nth_page(5)
		advancedPage.hide()		
		counterPage.hide()

		#Fill in the comboboxes

		#log type combobox

		liststore = gtk.ListStore(gobject.TYPE_STRING)
		print "ABC: ",self.logWriterHumanTypes
		for elem in self.logWriterHumanTypes:
			liststore.append([elem])

		self.logTypeCombo.set_model(liststore)
		self.logTypeCombo.set_active(0)

		cell = gtk.CellRendererText()
		self.logTypeCombo.pack_start(cell, True)
		self.logTypeCombo.add_attribute(cell, "text", 0)
		
		#scheduler combobox
		
		schedulerListStore = gtk.ListStore(gobject.TYPE_STRING)

		for elem in self.schedulerOptions:
			schedulerListStore.append([elem])

		self.schedulerCombo.set_model(schedulerListStore)
		self.schedulerCombo.set_active(0)

		self.schedulerCombo.pack_start(cell, True)
		self.schedulerCombo.add_attribute(cell, "text", 0)
		

		#downloader combobox
		
		downloaderListStore = gtk.ListStore(gobject.TYPE_STRING)

		for elem in self.downloaderOptions:
			downloaderListStore.append([elem])

		self.downloaderCombo.set_model(downloaderListStore)
		self.downloaderCombo.set_active(0)

		self.downloaderCombo.pack_start(cell, True)
		self.downloaderCombo.add_attribute(cell, "text", 0)

		#colour depth combobox
		
		colourDepthListStore = gtk.ListStore(gobject.TYPE_STRING)

		for elem in self.colourDepthOptions:
			colourDepthListStore.append([elem])

		self.colourDepthCombo.set_model(colourDepthListStore)
		self.colourDepthCombo.set_active(0)

		self.colourDepthCombo.pack_start(cell, True)
		self.colourDepthCombo.add_attribute(cell, "text", 0)

		#lift enable combobox
		
		liftEnableListStore = gtk.ListStore(gobject.TYPE_STRING)

		liftEnableOptions = ["True","False"]

		for elem in liftEnableOptions:
			liftEnableListStore.append([elem])

		self.liftEnableCombo.set_model(liftEnableListStore)
		self.liftEnableCombo.set_active(0)

		self.liftEnableCombo.pack_start(cell, True)
		self.liftEnableCombo.add_attribute(cell, "text", 0)

		#Media inventory combobox

		mediaInventoryListStore = gtk.ListStore(gobject.TYPE_STRING)

		mediaInventoryOptions = ["True","False"]

		self.mediaInventoryOptions = mediaInventoryOptions

		for elem in mediaInventoryOptions:
			mediaInventoryListStore.append([elem])

		self.mediaInventoryCombo.set_model(mediaInventoryListStore)
		self.mediaInventoryCombo.set_active(0)

		self.mediaInventoryCombo.pack_start(cell, True)
		self.mediaInventoryCombo.add_attribute(cell, "text", 0)


		#Set the range of values we accept for the spin controls

		width_adj = gtk.Adjustment(1024, 1.0, 10000, 1.0, 5.0, 0.0)
		height_adj = gtk.Adjustment(1024, 1.0, 10000, 1.0, 5.0, 0.0)
		queue_adj = gtk.Adjustment(10, 1.0, 10000, 1.0, 5.0, 0.0)
		refresh_adj = gtk.Adjustment(100, 1.0, 10000, 1.0, 5.0, 0.0)
		logLevel_adj = gtk.Adjustment(0, 0, 10, 1.0, 2.0, 0.0)
        	
		socketTime_adj = gtk.Adjustment(0, 0, 100, 1.0, 2.0, 0.0)
		frames_adj = gtk.Adjustment(0, 0, 100, 1.0, 2.0, 0.0)
		vwidth_adj = gtk.Adjustment(0, 0, 10000, 1.0, 2.0, 0.0)
		vheight_adj = gtk.Adjustment(0, 0, 10000, 1.0, 2.0, 0.0)
		vrotate_adj = gtk.Adjustment(0, -359, 359, 1.0, 2.0, 0.0)
		liftTrigger_adj = gtk.Adjustment(0, 0, 100, 1.0, 2.0, 0.0)

		osdBackOpacity_adj = gtk.Adjustment(70,1,100,1,2,0)
		osdFontSize_adj = gtk.Adjustment(270,24,400,1,5,0)

		osdWidth_adj = gtk.Adjustment(70,1,100,1,2,0)
		osdTimeout_adj = gtk.Adjustment(5,1,10,1,1,0)

		counterMax_adj = gtk.Adjustment(99,1,99,1,2,0)

		self.osdBackOpacitySpin.configure(osdBackOpacity_adj,0,0)
		self.osdFontSizeSpin.configure(osdFontSize_adj,0,0)
		self.osdWidthSpin.configure(osdWidth_adj,0,0)
		self.osdTimeoutSpin.configure(osdTimeout_adj,0,0)
		self.counterMaxSpin.configure(counterMax_adj,0,0)

		self.screenWidthText.configure(width_adj, 0, 0)
		self.screenWidthText.set_wrap(True)

		self.screenHeightText.configure(height_adj, 0, 0)
		self.screenHeightText.set_wrap(True)
		
		self.queueSizeText.configure(queue_adj, 0, 0)
		self.queueSizeText.set_wrap(True)

		self.refreshText.configure(refresh_adj, 0, 0)
		self.refreshText.set_wrap(True)

		self.logLevelSpin.configure(logLevel_adj, 0, 0)
		self.logLevelSpin.set_wrap(True)
	
		self.socketTimeSpin.configure(socketTime_adj,0,0)
		self.socketTimeSpin.set_wrap(True)

		self.framesSpin.configure(frames_adj,0,0)
		self.framesSpin.set_wrap(True)

		self.vwidthSpin.configure(vwidth_adj,0,0)
		self.vwidthSpin.set_wrap(True)

		self.vheightSpin.configure(vheight_adj,0,0)
		self.vheightSpin.set_wrap(True)

		self.vrotateSpin.configure(vrotate_adj,0,0)
		self.vrotateSpin.set_wrap(True)

		self.liftTriggerValue.configure(liftTrigger_adj,0,0)
		self.liftTriggerValue.set_wrap(True)

		#We want the labels to be translatable,
		#Using the Glade stuff grab the labels
		self.serverURLLabel = self.builder.get_object("serverURLLabel")
		self.clientIDLabel = self.builder.get_object("clientIDLabel")
		self.serverKeyLabel = self.builder.get_object("serverKeyLabel")
		self.refreshLabel = self.builder.get_object("refreshLabel")
		self.connectionLabel = self.builder.get_object("connectionLabel")
		self.fullscreenLabel = self.builder.get_object("fullscreenLabel")
		self.widthLabel = self.builder.get_object("widthLabel")
		self.heightLabel = self.builder.get_object("heightLabel")
		self.logLevelLabel = self.builder.get_object("logLevelLabel")
		self.logTypeLabel = self.builder.get_object("logTypeLabel")
		self.loggingFrameLabel = self.builder.get_object("loggingFrameLabel")
		self.statsFrameLabel = self.builder.get_object("statsFrameLabel")
		self.clientNameLabel = self.builder.get_object("clientNameLabel")

		#Labels for advanced options and tabs
		self.liftDefaultLabel = self.builder.get_object('liftDefaultLabel')
		self.lift7Label = self.builder.get_object('lift7Label')
		self.lift6Label = self.builder.get_object('lift6Label')
		self.lift5Label = self.builder.get_object('lift5Label')
		self.lift4Label = self.builder.get_object('lift4Label')
		self.lift3Label = self.builder.get_object('lift3Label')
		self.lift2Label = self.builder.get_object('lift2Label')
		self.lift1Label = self.builder.get_object('lift1Label')
		self.lift0Label = self.builder.get_object('lift0Label')
		self.tagLiftLabel = self.builder.get_object('tagLiftLabel')
		self.genLiftOptions = self.builder.get_object('genLiftOptions')
		self.firstSerialLabel = self.builder.get_object('firstSerialLabel')
		self.secondSerialLabel = self.builder.get_object('secondSerialLabel')
		self.liftTriggerLabel = self.builder.get_object('liftTriggerLabel')
		self.liftEnableLabel = self.builder.get_object('liftEnableLabel')
		self.liftOptionsLabel = self.builder.get_object('liftOptionsLabel')
		self.advancedOptionsLabel = self.builder.get_object('advancedOptionsLabel')
		self.otherSettingsLabel = self.builder.get_object('otherSettingsLabel')
		self.clientSettingsLabel = self.builder.get_object('clientSettingsLabel')
		self.serverSettingsLabel = self.builder.get_object('serverSettingsLabel')
		self.dateFormatLabel = self.builder.get_object('dateFormatLabel')
		self.schedulerLabel = self.builder.get_object('schedulerLabel')
		self.downloaderLabel = self.builder.get_object('downloaderLabel')
		self.libraryLabel = self.builder.get_object('libraryLabel')
		self.bppLabel = self.builder.get_object('bppLabel')
		self.socketTimeLabel = self.builder.get_object('socketTimeLabel')
		self.checksumLabel = self.builder.get_object('checksumLabel')
		self.lowTextureLabel = self.builder.get_object('lowTextureLabel')
		self.framesLabel = self.builder.get_object('framesLabel')
		self.vwidthLabel = self.builder.get_object('vwidthLabel')
		self.vheightLabel = self.builder.get_object('vheightLabel')
		self.vrotationLabel = self.builder.get_object('vrotationLabel')
		self.advancedOptionsCheck = self.builder.get_object("advancedOptionsCheck")

#		self.manualUpdateLabel = self.builder.get_object("manualUpdateLabel")
#		self.manualUpdateCombo = self.builder.get_object("manualUpdateCombo")
		self.xmdsLicenseKeyLabel = self.builder.get_object("xmdsLicenseKeyLabel")
		self.xmdsLicenseKeyEntry = self.builder.get_object("xmdsLicenseKeyEntry")

		self.onlineOpLabel = self.builder.get_object("onlineOpLabel")
		self.offlineOpLabel  = self.builder.get_object("offlineOpLabel")

		self.lift8Label = self.builder.get_object("lift8Label")
		self.lift9Label = self.builder.get_object("lift9Label")
		self.lift10Label = self.builder.get_object("lift10Label")
		self.lift11Label = self.builder.get_object("lift11Label")
		self.lift12Label = self.builder.get_object("lift12Label")
		self.lift13Label = self.builder.get_object("lift13Label")
		self.lift14Label = self.builder.get_object("lift14Label")
		self.lift15Label = self.builder.get_object("lift15Label")

		self.thirdSerialLabel = self.builder.get_object("thirdSerialLabel")
		self.fourthSerialLabel = self.builder.get_object("fourthSerialLabel")

		self.mediaInventoryLabel = self.builder.get_object("mediaInventoryLabel")

		self.counterTabLabel = self.builder.get_object("counterTabLabel")
		self.scanCodeNextLabel = self.builder.get_object("scanCodeNextLabel")
		self.scanCodeResetLabel = self.builder.get_object("scanCodeResetLabel")
		self.maxCounterLabel = self.builder.get_object("maxCounterLabel")

		self.popUpSettingsLabel = self.builder.get_object("popUpSettingsLabel")
		self.osdBackColourLabel = self.builder.get_object("osdBackColourLabel")
		self.osdBackOpacityLabel = self.builder.get_object("osdBackOpacityLabel")
		self.osdFontSizeLabel = self.builder.get_object("osdFontSizeLabel")
		self.osdFontColourLabel = self.builder.get_object("osdFontColourLabel")
		self.osdWidthLabel = self.builder.get_object("osdWidthLabel")
		self.osdTimeoutLabel = self.builder.get_object("osdTimeOutLabel")
		self.scanCodePrevLabel = self.builder.get_object("scanCodePrevLabel")

		#Now set the text in the labels. This is useful so that we can
		#then use this as a basis for translations on launchpad

#		self.manualUpdateLabel.set_text(_("Manual Update"))
		self.xmdsLicenseKeyLabel.set_text(_("xmdsLicenseKey"))

		self.serverURLLabel.set_text(_("Server URL"))
		self.clientIDLabel.set_text(_("Client ID"))
		self.serverKeyLabel.set_text(_("Server Key"))
		self.refreshLabel.set_text(_("Set the number of seconds between the client contacting the server for updates"))
		self.connectionLabel.set_text(_("Require connection to server"))
		self.fullscreenLabel.set_text(_("Fullscreen"))
		self.widthLabel.set_text(_("Width"))
		self.heightLabel.set_text(_("Height"))
		self.logLevelLabel.set_text(_("Log Level"))
		self.logTypeLabel.set_text(_("Log Type"))
		self.statsCaptureLabel.set_text(_("Statistics Capturing"))
		self.statsQueueSizeLabel.set_text(_("Queue Size"))
		self.loggingFrameLabel.set_text(_("Logging"))
		self.statsFrameLabel.set_text(_("Statistics Generation"))

		self.clientNameLabel.set_text(_("Client Name"))

		self.liftDefaultLabel.set_label(_('Default'))
		self.lift7Label.set_label(_('Lift 7'))
		self.lift6Label.set_label(_('Lift 6'))
		self.lift5Label.set_label(_('Lift 5'))
		self.lift4Label.set_label(_('Lift 4'))
		self.lift3Label.set_label(_('Lift 3'))
		self.lift2Label.set_label(_('Lift 2'))
		self.lift1Label.set_label(_('Lift 1'))
		self.lift0Label.set_label(_('Lift 0'))
		self.tagLiftLabel.set_label(_('Tagging Lift Options'))
		self.genLiftOptions.set_label(_('General Lift Options'))
		self.firstSerialLabel.set_label(_('1st Serial Port'))
		self.secondSerialLabel.set_label(_('2nd Serial Port'))
		self.liftTriggerLabel.set_label(_('Lift Trigger'))
		self.liftEnableLabel.set_label(_('Lift Enable'))
		self.liftOptionsLabel.set_label(_('Lift Options'))
		self.advancedOptionsLabel.set_label(_('Advanced Options'))
		self.otherSettingsLabel.set_label(_('Other Settings'))
		self.clientSettingsLabel.set_label(_('Client Settings'))
		self.serverSettingsLabel.set_label(_('Server Settings'))
		self.dateFormatLabel.set_label(_('Date Format'))
		self.schedulerLabel.set_label(_('Scheduler'))
		self.downloaderLabel.set_label(_('Downloader'))
		self.libraryLabel.set_label(_('Library Location'))
		self.bppLabel.set_label(_('Colour Depth (BPP)'))
		self.socketTimeLabel.set_label(_('Socket Timeout (s)'))
		self.checksumLabel.set_label(_('Checksum Downloaded Media'))
		self.lowTextureLabel.set_label(_('Low Texture Memory'))
		self.framesLabel.set_label(_('Frames per Second'))
		self.vwidthLabel.set_label(_('Virtual Width'))
		self.vheightLabel.set_label(_('Virtual Height'))
		self.vrotationLabel.set_label(_('Rotation'))

		self.onlineOpLabel.set_label(_("Online operation (syncronise with Xibo server)"))
#		self.offlineOpLabel.set_label(_("Offline operation (synchronise with USB memory stick)"))


		self.lift8Label.set_label(_("lift8"))
		self.lift9Label.set_label(_("lift9"))
		self.lift10Label.set_label(_("lift10"))
		self.lift11Label.set_label(_("lift11"))
		self.lift12Label.set_label(_("lift12"))
		self.lift13Label.set_label(_("lift13"))
		self.lift14Label.set_label(_("lift14"))
		self.lift15Label.set_label(_("lift15"))

		self.thirdSerialLabel.set_label(_("3rd Serial Port"))
		self.fourthSerialLabel.set_label(_("4th Serial Port"))

		self.mediaInventoryLabel.set_label(_("Media inventory"))

		self.counterTabLabel.set_label(_("Counter"))
		self.scanCodeNextLabel.set_label(_("Increment counter\nscan code"))
		self.scanCodePrevLabel.set_label(_("Decrement counter\nscan code"))
		self.scanCodeResetLabel.set_label(_("Reset counter\nscan code"))
		self.maxCounterLabel.set_label(_("Maximum counter\nscan code"))

		self.popUpSettingsLabel.set_label(_("Pop-up settings"))
		self.osdBackColourLabel.set_label(_("Background\ncolour"))
		self.osdBackOpacityLabel.set_label(_("Opacity"))
		self.osdFontSizeLabel.set_label(_("Fontsize"))
		self.osdFontColourLabel.set_label(_("Font colour"))
		self.osdWidthLabel.set_label(_("Width"))
		self.osdTimeoutLabel.set_label(_("Timeout"))

		#Set the icon for the Window
		self.window.set_icon_from_file("xibo.ico")


		#Now set the labels of the buttons and window
		
		self.clearButton.set_label(_("Clear Form"))
		self.saveButton.set_label(_("Save Config"))
		self.window.set_title(_("Xibo Client Configuration"))


		#Set up the combo box

#		manualUpdateListStore = gtk.ListStore(gobject.TYPE_STRING)

#		for elem in self.manualUpdateOptions:
#			manualUpdateListStore.append([elem])

#		self.manualUpdateCombo.set_model(manualUpdateListStore)
#		self.manualUpdateCombo.set_active(1)

#		self.manualUpdateCombo.pack_start(cell, True)
#		self.manualUpdateCombo.add_attribute(cell, "text", 0)

		logFilePath = os.path.join(os.path.abspath(''),self.pyClientLogName)

		self.logFileLinkButton.set_uri("file:%s%s%s"%(os.sep,os.sep,logFilePath))

#		print "File path: ", logFilePath

		#Set the tick box to online operation
		self.offlineCheckButton.set_active(True)
		self.offlineCheckButton.set_active(False)

		#Set tooltips
		self.set_tooltips()

		self.window.show()

		#Check that the directory exists where the configuration file
		#is stored.

		if os.path.exists(self.pyclientConfPath):
			if os.path.isfile(self.pyclientConfPath):

				self.logger1.error("Python client path chosen is a file")

				print "Location is a file."
				self.errorDialog.set_markup(_("File path is a file. Cannot write to it"))
				self.errorDialog.show()
				print "Exiting gracefully"
#				sys.exit()
			elif os.path.isdir(self.pyclientConfPath):
				self.logger1.info("Python client path chosen is available")
				print "Location exists."
				print "Carrying on..."		

				self.pyClientConfName = os.path.join(self.pyclientConfPath,self.pyClientConfName)				
		else:
			print "Configuration directory does not exist"
			self.logger1.warning("Python client path chosen does not exist")
			try:
				os.makedirs(self.pyclientConfPath)
				print "Directory created"
				self.logger1.info("Python client path chosen has been created")
				self.pyClientConfName = os.path.join(self.pyclientConfPath,self.pyClientConfName)
			except OSError:
				self.logger1.error("Python client path chosen could not be created")
				self.errorDialog.set_markup(_("File path could not be created"))
				self.errorDialog.show()


		#Check that a file can be written to this directory
		try:
			file_written = open(os.path.join(self.pyclientConfPath,"tmp"),"w")
			file_written.close()
		except:
			self.logger1.error("Could not write to testing file")			
		
		is_file = os.path.isfile(os.path.join(self.pyclientConfPath,"tmp"))
		
		self.logger1.info("Testing file has been created in the chosen location")
		
		#Check that the file can be written to

		try:
			file_edit = open(os.path.join(self.pyclientConfPath,"tmp"),"w")
			file_edit.write("tmp")
			file_edit.close()
			print "boo"
		except:
			self.logger1.info("Testing file could not be written to")
			
		is_data = False
		data = None

		try:
			data = open(os.path.join(self.pyclientConfPath,"tmp"),"r").read()
		except:
			self.logger1.error("Cannot open testing file to read data")
		if data == "tmp":
			is_data = True
			self.logger1.info("Testing file could be written to")
		else:
			self.logger1.info("Testing file could not be written to")

		#Check that the file can be deleted
		is_deleted = False
		try:
			os.remove(os.path.join(self.pyclientConfPath,"tmp"))
		except:
			self.logger1.error("Cannot delete testing file")

		if os.path.isfile(os.path.join(self.pyclientConfPath,"tmp")) == False:
			is_deleted = True
			self.logger1.info("Testing file has been deleted successfully")

		if is_deleted and is_data and is_file:
			print "Location is acceptable for file writing"
			self.logger1.info("Location is acceptable for file writing")
			self.messageDialog.set_markup(_("File location is acceptable"))
			self.messageDialog.show()

		else:
			print "Cannot write to file"
			self.logger1.error("Location selected is not acceptable for file writing")
			print "Exiting gracefully"
			self.errorDialog.show()
			self.errorDialog.set_markup(_("Cannot write to file"))
#			sys.exit()



		print self.pyClientConfName


		if is_deleted and is_data and is_file:

			#Read the configuration information from the configuration file
			self.readConfig()

		#Check to see if the client ID field is blank. 
		#If so, then generate one

		if self.clientIDText.get_text() == "":
			uuid = self.genClientID()
			self.clientIDText.set_text(str(uuid))		

	def messageDialogExit(self,widget):
		sys.exit()

	def infoDialogOKSignal(self,widget):
		self.messageDialog.hide()

	def offlineOperationToggle(self,widget):
		
		offlineOperation = widget.get_active()

		self.logger8.info(_("Offline operation checkbox toggled"))

		if offlineOperation:
			print "Offline operation selected"
#			self.manualUpdateCombo.set_sensitive(True)
		#	self.xmdsLicenseKeyEntry.set_sensitive(True)

			self.logger8.info(_("Offline operation selected"))

			self.serverURLText.set_sensitive(False)
			self.clientIDText.set_sensitive(False)
			self.serverKeyText.set_sensitive(False)
			self.clientNameText.set_sensitive(False)
			
		else:
			print "Online operation selected"
			self.logger8.info(_("Online operation selected"))
#			self.manualUpdateCombo.set_sensitive(False)
		#	self.xmdsLicenseKeyEntry.set_sensitive(False)
			
			self.serverURLText.set_sensitive(True)
			self.clientIDText.set_sensitive(True)
			self.serverKeyText.set_sensitive(True)
			self.clientNameText.set_sensitive(True)			
			
	def on_advancedOptionsCheck(self,widget):
		"""Function called when advanced options checkbox is toggled.
		Used to hide / display the advanced notebook tab"""

		advancedPage = self.notebook1.get_nth_page(3)		
		counterPage = self.notebook1.get_nth_page(5)

		if self.advancedOptionsCheck.get_active() and self.advancedTabVisible == False:
			advancedPage.show()
			counterPage.show()
			self.advancedTabVisible = True
			self.logger6.info(_("advancedTabEnabled"))
			self.logger6.info(_("counterTabEnabled"))

		
		elif self.advancedOptionsCheck.get_active() == False and self.advancedTabVisible:
			advancedPage.hide()
			counterPage.hide()
			self.advancedTabVisible = False
			self.logger6.info(_("advancedTabDisabled"))
			self.logger6.info(_("counterTabDisabled"))

	def readConfigAppConf(self):
		"""This reads the configuration file that is used by the configuration application"""
		self.logger7.info(_("Configuration application configuration file being read in"))
		config_file = ""
		try:
			config_file = open(self.clientConfFile,"r")

			#Implement all the stuff to read the config file in
			data = config_file.read()
			config_file.close()
			self.logger7.info(_("Reading configuration file to make sure file is not empty"))
			#If the file is not empty, then try and process it

			if len(data) != 0:
				config = ConfigParser.ConfigParser()
				config.read(self.clientConfFile)

				self.logger7.info(_("Reading configuration file"))

				#Get the information from the configuration file
				#and display into the GUI
				
				#Xibo client configuration file location
				xiboClientConf = None

				try:
					xiboClientConf = config.get('Main','clientConfName')
				except:
					xiboClientConf = "site.cfg"
					
				self.logger7.info(_("Client configuration: %s"%xiboClientConf))				

				#Options pertaining to log type
				logTypeOptions = config.get("Options","logType").split(",")
				for i in range(len(logTypeOptions)):
					logTypeOptions[i] = _(logTypeOptions[i])

				print logTypeOptions

				#Options pertaining to log type (human readable form)
				logTypeHumanOptions = config.get("Options","logTypeHuman").split(",")

				for i in range(len(logTypeHumanOptions)):
					logTypeHumanOptions[i] = _(logTypeHumanOptions[i])

				self.logger7.info(_("logTypeOptions: %s"%logTypeOptions))

				self.logger7.info(_("logTypeHumanOptions: %s"%logTypeHumanOptions))

				#Options pertaining to scheduler
				schedulerOptions = config.get("Options","scheduler").split(",")
				for i in range(len(schedulerOptions)):
					schedulerOptions[i] = _(schedulerOptions[i])

				print schedulerOptions

				self.logger7.info(_("schedulerOptions: %s"%schedulerOptions))
				

				#Options pertaining to downloader
				downloaderOptions = config.get("Options","downloader").split(",")
				for i in range(len(downloaderOptions)):
					downloaderOptions[i] = _(downloaderOptions[i])

				print downloaderOptions

				self.logger7.info(_("downloaderOptions: %s"%downloaderOptions))

				#Options pertaining to colour depth (BPP)
				colourDepthOptions = config.get("Options","colourDepth").split(",")
				for i in range(len(colourDepthOptions)):
					colourDepthOptions[i] = _(colourDepthOptions[i])

				print colourDepthOptions

				self.logger7.info(_("colourDepthOptions: %s"%colourDepthOptions))

				clientConfLoc = None
				
				try:
					clientConfLoc = config.get("Main","clientConfLoc")
				except:
					clientConfLoc = os.path.expanduser('~/.xibo')
					
				clientConfName = None
				try:
					clientConfName = config.get("Main","clientConfName")
				except:
					clientConfName = "site.cfg"
					
					
				self.logger7.info(_("clientConfLocation: %s"%clientConfLoc))
				self.logger7.info(_("clientConfName: %s"%clientConfName))


				return {"xiboClientConf":xiboClientConf,"logTypeOptions":logTypeOptions,"logTypeHumanOptions":logTypeHumanOptions,"clientConfLoc":clientConfLoc,"clientConfName":clientConfName,"schedulerOptions":schedulerOptions,"downloaderOptions":downloaderOptions,"colourDepthOptions":colourDepthOptions}

			else:
				self.logger7.error("Configuration file is empty. Cannot continue")
				self.errorDialog.set_markup(_("The configuration application configuration file is empty. Cannot continue"))
				self.errorDialog.show()

		except:
			print "Could not open the configuration application configuration file"

			self.logger7.error(_("Could not open configuration file. Cannot continue"))

			self.errorDialog.set_markup(_("Could not open the configuration application configuration file"))
			self.errorDialog.show()
			return -1

	def clearFormSignal(self,widget,data=None):
		
		self.serverURLText.set_text("")
		self.clientIDText.set_text("")
		self.serverKeyText.set_text("")
		self.refreshText.set_text("")
		self.serverConnBool.set_active(False)
		self.fullScreenBool.set_active(False)
		self.screenWidthText.set_text("")
		self.screenHeightText.set_text("")
		self.captureStatisticsBool.set_active(False)
		self.queueSizeText.set_text("")

		self.screenWidthText.set_value(0)
		self.screenHeightText.set_value(0)
		self.queueSizeText.set_value(0)


		self.clearButton.set_tooltip_text(_("Clear input fields"))
		self.saveButton.set_tooltip_text(_("Save data to file")) 

		self.logLevelSpin.set_value(0)
		
		self.logTypeCombo.set_active(0) 
		self.liftEnableCombo.set_active(0)
		self.schedulerCombo.set_active(0)
		self.downloaderCombo.set_active(0)
		self.colourDepthCombo.set_active(0)
#		self.manualUpdateCombo.set_active(0)

		
		self.checksumCheckButton.set_active(False) 
		self.lowTextureCheckButton.set_active(False)
	
		self.clientNameText.set_text("") 

		#Advanced options widgets

		self.liftDefaultTagText.set_text("") 
		self.lift7TagText.set_text("")
		self.lift6TagText.set_text("")
		self.lift5TagText.set_text("")
		self.lift4TagText.set_text("")
		self.lift3TagText.set_text("")
		self.lift2TagText.set_text("")
		self.lift1TagText.set_text("")
		self.lift0TagText.set_text("")
		self.firstSerialText.set_text("")
		self.secondSerialText.set_text("")
		self.liftTriggerValue.set_value(0) 

		self.dateFormatEntry.set_text("") 
		self.libraryEntry.set_text("")
		self.socketTimeSpin.set_value(0)

		self.framesSpin.set_value(0) 
		self.vwidthSpin.set_value(0)
		self.vheightSpin.set_value(0)
		self.vrotateSpin.set_value(0)

		self.xmdsLicenseKeyEntry.set_text("")
		
		self.lift8TagText.set_text("")
		self.lift9TagText.set_text("")
		self.lift10TagText.set_text("")
		self.lift11TagText.set_text("")
		self.lift12TagText.set_text("")
		self.lift13TagText.set_text("")
		self.lift14TagText.set_text("")
		self.lift15TagText.set_text("")

		self.thirdSerialText.set_text("")
		self.fourthSerialText.set_text("")

		self.osdFontColourText.set_text("")

		self.mediaInventoryCombo.set_active(0)

		self.scanCodeNextText.set_text("")
		self.scanCodePrevText.set_text("")

		self.scanCodeResetText.set_text("")
		self.counterMaxSpin.set_value(0)

		self.osdBackColourText.set_text("")
		self.osdBackOpacitySpin.set_value(0)
		self.osdFontSizeSpin.set_value(0)
		self.osdWidthSpin.set_value(0)
		self.osdTimeoutSpin.set_value(0)



		self.logger9.info("Clearing form elements")

	def logTypeComboChanged(self,widget,data=None):

		model = widget.get_model()
		index = widget.get_active()
		logTypeText = model[index][0].lower()

		if logTypeText == "local file":
			#Check to see if the file pointed to by the link exists
			error_file = self.logFileLinkButton.get_uri().split(":%s%s"%(os.sep,os.sep))[1]
			if os.path.isfile(error_file):
				self.logFileLinkButton.show()
		else:
			self.logFileLinkButton.hide()

		val = widget.get_active()


	def onDestroy(self,widget,data=None):
		"""
		Close the program. Executes when the main
		window is destroyed
		"""
		self.logger10.info("Exiting program")
		gtk.main_quit()


	def confValErr(self,err,logger):
		#print "Error finding config. value in file: %s"%err
		#self.logger2.warning("%s item not in config. file"%err)
		logger.warning("%s item not in config. file"%err)
		
	def readConfig(self):
		"""Function used to read in the configuration file and
		fill in the GUI text elements"""

		#Firstly check if the configuration file exists. If it does then
		#open it and extract the values. These can then be filled into the
		#fields on the GUI

		#Try opening the configuration file, if it does not exists, then
		#create it

		config_file = ""
		try:
			config_file = open(self.pyClientConfName,"r")

			self.logger2.info("Config. file opened successfully")

			#Implement all the stuff to read the config file in
			data = config_file.read()
			config_file.close()
			#If the file is not empty, then try and process it

			if len(data) != 0:
				self.logger2.info("Config. data read in successfully")


				self.readDataFromConfigFile(self.pyClientConfName,self.logger2)

				
		except IOError:
			print "Cannot open"
			self.logger2.warning("Cannot open configuration file")
			#Read in the values from the site.cfg.default

			self.readDataFromConfigFile(self.pyClientConfDefaultsName,self.logger12,defaults=True)
			self.messageDialog.set_markup(_("Could not open configuration file. A new one will be created"))
			self.messageDialog.show()

			
			

	def readDataFromConfigFile(self,confFileName,logger,defaults=False):


		config = ConfigParser.ConfigParser()
		config.read(confFileName)

		#Get the information from the configuration file
		#and display into the GUI

		try:
			self.serverURLText.set_text(config.get('Main','xmdsUrl'))
			logger.info("serverURL: %s"%config.get('Main','xmdsUrl'))
		except:
			self.confValErr('xmdsUrl',logger)

		if defaults == False:
			try:
				self.clientIDText.set_text(config.get("Main","xmdsClientID"))
				logger.info("clientID: %s"%config.get('Main','xmdsClientID'))
			except:
				self.confValErr("xmdsClientID",logger)
				logger.warning("xmdClientID item not in config. file")

		try:
			self.serverKeyText.set_text(config.get('Main','xmdsKey'))
			logger.info("xmdsKey: %s"%config.get('Main','xmdsKey'))
		except:
			self.confValErr('xmdsKey',logger)

		try: 
			self.refreshText.set_text(config.get('Main','xmdsUpdateInterval'))
			logger.info("xmdsUpdateInterval: %s"%config.get('Main','xmdsUpdateInterval'))
		except:
			self.confValErr('xmdsUpdateInterval',logger)

		try:
			self.clientNameText.set_text(config.get('Main','xmdsClientName'))
			logger.info("xmdsClientName: %s"%config.get('Main','xmdsClientName'))
		except:
			self.confValErr('xmdsClientName',logger)			


		try:
			requireXmds = False
			if config.get('Main','requireXmds') == "true":
				requireXmds = True

			self.serverConnBool.set_active(requireXmds)
			logger.info("requireXMDS: %s"%requireXmds)

		except:
			self.confValErr("requireXmds",logger)

		try:
			fullScreen = False
			if config.get('Main','fullscreen') == "true":
				fullScreen = True
			self.fullScreenBool.set_active(fullScreen)
			logger.info("fullscreen: %s"%fullscreen)
		

		except:
			self.confValErr("fullscreen",logger)					

		try:
			captureStats = False
			if config.get('Stats','collect') == "true":
				captureStats = True
			logger.info("captureStats: %s"%captureStats)

			self.captureStatisticsBool.set_active(captureStats)
		except:
			self.confValErr("Stats - Collect",logger)


		try:
			self.screenWidthText.set_value(int(config.get('Main','width')))
			logger.info("screenWidth: %s"%config.get('Main','width'))

		except:
			self.confValErr("width",logger)

		try:
			self.screenHeightText.set_value(int(config.get('Main','height')))
			logger.info("screenHeight: %s"%config.get('Main','height'))

		except:
			self.confValErr("height",logger)

		try:
			self.queueSizeText.set_value(int(config.get('Stats','queueSize')))
			logger.info("queueSize: %s"%config.get('Stats','queueSize'))

		except:
			self.confValErr("queueSize",logger)

		try:
			self.logLevelSpin.set_value(int(config.get('Logging','logLevel')))
			logger.info("Logging level: %s"%config.get('Logging','logLevel'))
		
		except:
			self.confValErr("logLevel",logger)

		try:				
			logType = config.get('Logging','logWriter')

			val = 0

			for elem in self.logWriterTypes:
				if elem.lower() == logType.lower():
					print elem.lower(), logType.lower()
					break
				val += 1
			print "*"*len(str(self.logWriterTypes))
			print logType
			print self.logWriterTypes
			print " "*(len(str(self.logWriterTypes))/2),val
			print self.logWriterHumanTypes
			print "*"*len(str(self.logWriterTypes))

			logger.info("logWriter: %s"%self.logWriterTypes[val])
			logger.info("logWriterHuman: %s"%self.logWriterHumanTypes[val])
			self.logTypeCombo.set_active(val)				
		except:
			self.confValErr("logWriter",logger)
	

		#Advanced options

		try:
			self.dateFormatEntry.set_text(config.get("TickerMedia","dateFormat"))
			logger.info("tickerMedia: %s"%config.get('TickerMedia','dateFormat'))

		except:
			self.confValErr("dateFormat",logger)

		try:
			self.libraryEntry.set_text(config.get("Main","libraryDir"))
			logger.info("libraryDir: %s"%config.get('Main','libraryDir'))

		except:
			self.confValErr("libraryDir",logger)

		try:
			self.socketTimeSpin.set_value(int(config.get("Main","socketTimeout")))
			logger.info("socketTimeout: %s"%config.get('Main','socketTimeout'))

		except:
			self.confValErr("socketTimeout",logger)

		try:
			self.framesSpin.set_value(int(config.get("Main","fps")))
			logger.info("FPS: %s"%config.get('Main','fps'))
		
		except:
			self.confValErr("fps",logger)					

		try:
			self.vwidthSpin.set_value(int(config.get("Main","vwidth")))
			logger.info("VirtualWidth: %s"%config.get('Main','vwidth'))

		except:
			self.confValErr("vwidth",logger)

		try:
			self.vheightSpin.set_value(int(config.get("Main","vheight")))
			logger.info("VirtualHeight: %s"%config.get('Main','vheight'))

		except:
			self.confValErr("vheight",logger)

		try:
			self.vrotateSpin.set_value(int(config.get("Main","vrotation")))
			logger.info("VirtualRotation: %s"%config.get('Main','vrotation'))

		except:
			self.confValErr("vrotation",logger)


		try:
			self.xmdsLicenseKeyEntry.set_text(config.get("Main","xmdsLicenseKey"))
			logger.info("xmdsLicenseKey: %s"%config.get('Main','xmdsLicenseKey'))

		except:
			self.confValErr('xmdsLicenseKey',logger)


		#Sort out the combo boxes

		try:
			schedType = config.get("Main","Scheduler")

			val = 0
			for elem in self.schedulerOptions:
				if elem.lower() == schedType.lower():
					break
				val += 1
			logger.info("scheduler: %s"%self.schedulerOptions[val])

			self.schedulerCombo.set_active(val)
		except:
			self.confValErr("scheduler",logger)
	
		try:
			dloadType = config.get("Main","Downloader")

			val = 0
			for elem in self.downloaderOptions:
				if elem.lower() == dloadType.lower():
					break
				val += 1
			logger.info("downloader: %s"%self.downloaderOptions[val])

			self.downloaderCombo.set_active(val)
		except:
			self.confValErr("downloader",logger)
	
		try:
			bppType = config.get("Main","bpp")

			val = 0

			for elem in self.colourDepthOptions:
				if elem.lower() == bppType.lower():
					break
				val += 1
			logger.info("BPP: %s"%self.colourDepthOptions[val])

			self.colourDepthCombo.set_active(val)
		except:
			self.confValErr("bpp",logger)

		#USB update section
		try:
			manualUpdateType = config.get("Main","manualUpdate")
			logger.info("offlineUpdate: %s"%manualUpdateType)

			if manualUpdateType == "true":
				manualUpdateType = True
			elif manualUpdateType == "false":
				manualUpdateType = False

			if manualUpdateType == True or manualUpdateType == False:
				if manualUpdateType == True:
					print "Stuff done"
					self.offlineCheckButton.set_active(True)
					self.offlineOperationToggle(self,self.offlineCheckButton)

		except:
			self.confValErr('offlineUpdate',logger)
			print "Manual Update Failed"
		
		#Now the check boxes

		checksum = False
		try:
			if config.get('Main','checksumPreviousDownloads') == "true":
				checksum = True
			
			logger.info("checksumPreviousDownloads: %s"%checksum)

		except:
			self.confValErr("checksumPreviousDownloads",logger)


		lowTexture = False

		try:
			if config.get('Main','lowTextureMemory') == "true":
				lowTexture = True
			logger.info("lowTextureMemory: %s"%lowTexture)

		except:
			self.confValErr("lowTextureMemory",logger)	


		self.checksumCheckButton.set_active(checksum)

		self.lowTextureCheckButton.set_active(lowTexture)


		#Now the lift options
		try:
			self.liftDefaultTagText.set_text(config.get("LiftTags","default"))
			logger.info("DefaultLiftTag: %s"%config.get('LiftTags','default'))

		except:
			self.confValErr("liftTags",logger)

		try:
			self.lift7TagText.set_text(config.get("LiftTags","lift7"))
			logger.info("Lift7Tag: %s"%config.get('LiftTags','lift7'))

		except:
			self.confValErr("lift7",logger)

		try:
			self.lift6TagText.set_text(config.get("LiftTags","lift6"))
			logger.info("Lift6Tag: %s"%config.get('LiftTags','lift6'))
		except:
			self.confValErr("lift6",logger)

		try:
			self.lift5TagText.set_text(config.get("LiftTags","lift5"))
			logger.info("Lift5Tag: %s"%config.get('LiftTags','lift5'))
		except:
			self.confValErr("lift5",logger)

		try:
			self.lift4TagText.set_text(config.get("LiftTags","lift4"))
			logger.info("Lift4Tag: %s"%config.get('LiftTags','lift4'))
		except:
			self.confValErr("lift4",logger)

		try:
			self.lift3TagText.set_text(config.get("LiftTags","lift3"))
			logger.info("Lift3Tag: %s"%config.get('LiftTags','lift3'))
		except:
			self.confValErr("lift3",logger)

		try:
			self.lift2TagText.set_text(config.get("LiftTags","lift2"))
			logger.info("Lift2Tag: %s"%config.get('LiftTags','lift2'))
		except:
			self.confValErr("lift2",logger)

		try:
			self.lift1TagText.set_text(config.get("LiftTags","lift1"))
			logger.info("Lift1Tag: %s"%config.get('LiftTags','lift1'))
		except:
			self.confValErr("lift1",logger)

		try:
			self.lift0TagText.set_text(config.get("LiftTags","lift0"))
			logger.info("Lift0Tag: %s"%config.get('LiftTags','lift0'))
		except:
			self.confValErr("lift0",logger)

		try:
			self.firstSerialText.set_text(config.get("Lift","serial0"))
			logger.info("FirstSerial: %s"%config.get('Lift','serial0'))
		except:
			self.confValErr("serial0",logger)

		try:
			self.secondSerialText.set_text(config.get("Lift","serial1"))
			logger.info("SecondSerial: %s"%config.get('Lift','serial1'))
		except:
			self.confValErr("serial1",logger)

		try:
			self.liftTriggerValue.set_value(int(config.get("Lift","trigger")))
			logger.info("LiftTrigger: %s"%config.get('Lift','trigger'))
		except:
			self.confValErr("trigger",logger)				

		try:

			liftEnableType = config.get("Lift","enabled")
			logger.info("LiftEnabled: %s"%config.get('Lift','enabled'))

			val = 0

			for elem in self.liftEnableOptions:
				if elem.lower() == liftEnableType.lower():
					break
				val += 1

			self.liftEnableCombo.set_active(val)
		except:
			self.confValErr("liftEnabled",logger)


		#Now do the new options (extra lift and counter specifically)

#		try:
#			self.mediaInventoryCombo.set_value(int(config.get("Main","mediaInventory")))
#		except:
#			self.confValErr("mediaInventory",logger)

		try:
			mediaInv = config.get("Main","mediaInventory")

			val = 0
			for elem in self.mediaInventoryOptions:
				if elem.lower() == mediaInv.lower():
					break
				val += 1
			logger.info("scheduler: %s"%self.mediaInventoryOptions[val])

			self.mediaInventoryCombo.set_active(val)
		except:
			self.confValErr("mediaInventory",logger)


		try:
			self.scanCodePrevText.set_text(config.get("TicketCounter","prevScanCode"))
		except:
			self.confValErr("prevScanCode",logger)

		try:
			self.scanCodeNextText.set_text(config.get("TicketCounter","nextScanCode"))
		except:
			self.confValErr("nextScanCode",logger)

		try:
			self.scanCodeResetText.set_text(config.get("TicketCounter","resetScanCode"))
		except:
			self.confValErr("resetScanCode",logger)

		try:
			self.osdBackColourText.set_text(config.get("TicketCounter","osdBackColour"))
		except:
			self.confValErr("osdBackColour",logger)

		try:
			self.osdFontColourText.set_text(config.get("TicketCounter","osdFontColour"))
		except:
			self.confValErr("osdFontColour",logger)

		try:
			self.lift8TagText.set_text(config.get("LiftTags","lift8"))
		except:
			self.confValErr("lift8",logger)

		try:
			self.lift9TagText.set_text(config.get("LiftTags","lift9"))
		except:
			self.confValErr("lift9",logger)

		try:
			self.lift10TagText.set_text(config.get("LiftTags","lift10"))
		except:
			self.confValErr("lift10",logger)

		try:
			self.lift11TagText.set_text(config.get("LiftTags","lift11"))
		except:
			self.confValErr("lift11",logger)

		try:
			self.lift12TagText.set_text(config.get("LiftTags","lift12"))
		except:
			self.confValErr("lift12",logger)

		try:
			self.lift13TagText.set_text(config.get("LiftTags","lift13"))
		except:
			self.confValErr("lift13",logger)

		try:
			self.lift14TagText.set_text(config.get("LiftTags","lift14"))
		except:
			self.confValErr("lift14",logger)

		try:
			self.lift15TagText.set_text(config.get("LiftTags","lift15"))
		except:
			self.confValErr("lift15",logger)

		try:
			self.thirdSerialText.set_text(config.get("Lift","serial2"))
		except:
			self.confValErr("3rdSerial",logger)

		try:
			self.fourthSerialText.set_text(config.get("Lift","serial3"))
		except:
			self.confValErr("4thSerial",logger)

		try:
			self.counterMaxSpin.set_value(int(config.get("TicketCounter","maxCount")))
		except:
			self.confValErr("maxCount",logger)

		#Multiply the opacity by 100 to turn into a percentage
#		try:
		if 1:
			self.osdBackOpacitySpin.set_value(float(config.get("TicketCounter","osdBackOpacity"))*100)
#		except:
#			self.confValErr("osdBackOpacity",logger)

		try:
			self.osdFontSizeSpin.set_value(int(config.get("TicketCounter","osdFontSize")))
		except:
			self.confValErr("osdFontSize",logger)

		try:
			self.osdWidthSpin.set_value(int(config.get("TicketCounter","osdWidthPercent")))
		except:
			self.confValErr("osdWidthPercent",logger)
	
		#Divide by 1000 to turn the value from seconds to milliseconds
		try:
			self.osdTimeoutSpin.set_value(int(config.get("TicketCounter","osdTimeOut"))/1000)
		except:
			self.confValErr("osdTimeOut",logger)


	def checkDataSensible(self,configValues):

		scanCodes = []

		scanCodes.append(configValues["nextScanCode"][1])
		scanCodes.append(configValues["prevScanCode"][1])
		scanCodes.append(configValues["resetScanCode"][1])

		if scanCodes[0] == scanCodes[1] or scanCodes[1] == scanCodes[2] or scanCodes[0] == scanCodes[2]:
	
			return "scanCodes"
		else:
			return True

	def saveConfigSignal(self,widget,data=None):
		a = self.getConfValues()
		self.logger11.info("Config Values to process: %s"%a)

		#Before we write the data to the file, we want to check to see if these data make sense.
		#Invoke a function to check the data entered is sensible. True indicates correct data

		dataCheck = self.checkDataSensible(a)

		if dataCheck != True:
			#Make a note and warn the user
			if dataCheck == "scanCodes":
				self.messageDialog.set_markup(_("Two or more scan codes are the same. Please correct this before saving"))
				self.messageDialog.show()
		
		else:
			config = ConfigParser.RawConfigParser()

			config.optionxform = str

			configOptions = ["Main", "Logging", "Stats", "TickerMedia", "Lift", "LiftTags","TicketCounter"]

			for configOption in configOptions:
				#print configOption
				config.add_section(configOption)

				for elem in a:
					#print elem, a[elem][1], configOption
					if a[elem][0] == configOption:
						print elem, a[elem][1],configOption
						try:

							config.set(configOption, elem, str(a[elem][1]))
							self.logger11.info("Value: %s %s %s"%(configOption,elem,str(a[elem][1])))		
						except:
							print "Error setting option:"
							print "Element:", elem
							print "Data:", a[elem]
							print "Error setting: %s, %s"%(elem,a[elem][1])
							print a[elem][1]
							print str(a[elem][1])
							self.logger11.error("Error setting value: %s %s %s"%(configOption,elem,str(a[elem][1])))
						finally:
							#Write everything, barring the error item

						#	with open(self.pyClientConfName, 'wb') as configfile:
						#		config.write(configfile)

							try:
								configfile = open(self.pyClientConfName,"wb")
								config.write(configfile)
								self.logger11.info("Data successfully written")
								self.messageDialog.set_markup(_("Successfully written configuration file"))
								self.messageDialog.show()

							except:
								self.logger11.error("Data could not be written")
								self.errorDialog.set_markup(_("Could not open / write to configuration file. Cannot continue"))
								self.errorDialog.show()

#		#Read in the existing configuration file as a string
#		#we can then replace every instance of %s with one of the
#		#configuration items

#		#I have chosen this way because then we can keep the comments
#		#in place for manual usage
	
#		config_template_string = ""
#		try:
#			f = open("site.cfg.default","r")
#			config_template_string = f.read()
#			f.close()
#		except:
#			print "Error reading default config file"

		#Now create the string to write to the new config. file

#		config_string = config_template_string%(a["serverURL"],a["clientID"],a["serverKey"],a["refresh"],a["serverConn"],a["screenWidth"],a["screenHeight"],a["fullScreen"],a["logType"],a["logVal"],a["captureStats"],a["queueSize"])

#		#Now write the configuration file

#		try:
#			f = open(self.pyClientConfLoc,"w")
#		#	f.write(config_string)
#			f.close()
#		except:
#			print "Could not write configuration file"

	def genClientID(self):
		"""Function used to generate a random client ID. Returns a generated UUID"""
		uuidStr = uuid.uuid4()
		self.logger4.info("UUID Generated: %s"%uuidStr)
		return uuidStr


	def set_tooltips(self):

		self.clearButton.set_tooltip_text(_("Clear input fields"))
		self.saveButton.set_tooltip_text(_("Save data to file")) 

		self.serverURLText.set_tooltip_text(_("URL of your Xibo server")) 
		self.clientIDText.set_tooltip_text(_("Client identifier (used to generate license key hash)")) 
		self.serverKeyText.set_tooltip_text(_("Server key")) 
		self.refreshText.set_tooltip_text(_("Collection interval")) 
		self.serverConnBool.set_tooltip_text(_("Does the client have to connect to XMDS before playing cached content?")) 
		self.fullScreenBool.set_tooltip_text(_("Should the client run fullscreen"))
		self.screenWidthText.set_tooltip_text(_("Width of the rendered output screen")) 
		self.screenHeightText.set_tooltip_text(_("Height of the rendered output screen")) 
		self.captureStatisticsBool.set_tooltip_text(_("States whether statistics are generated or not")) 
		self.queueSizeText.set_tooltip_text(_("Statistics queue size")) 
		self.logLevelSpin.set_tooltip_text(_("Amount of log data to write. The higher the number, the more is written")) 
		self.logTypeCombo.set_tooltip_text(_("Where log data should be written to")) 
		self.clientNameText.set_tooltip_text(_("Name as it will be displayed in the server app")) 

		#Advanced options widgets

		self.liftDefaultTagText.set_tooltip_text(_("Tag associated with lift input")) 
		self.lift7TagText.set_tooltip_text(_("Tag associated with lift input")) 
		self.lift6TagText.set_tooltip_text(_("Tag associated with lift input")) 
		self.lift5TagText.set_tooltip_text(_("Tag associated with lift input")) 
		self.lift4TagText.set_tooltip_text(_("Tag associated with lift input"))
		self.lift3TagText.set_tooltip_text(_("Tag associated with lift input")) 
		self.lift2TagText.set_tooltip_text(_("Tag associated with lift input")) 
		self.lift1TagText.set_tooltip_text(_("Tag associated with lift input")) 
		self.lift0TagText.set_tooltip_text(_("Tag associated with lift input")) 
		self.firstSerialText.set_tooltip_text(_("First serial port to use for lift purposes")) 
		self.secondSerialText.set_tooltip_text(_("First serial port to use for lift purposes")) 
		self.liftTriggerValue.set_tooltip_text(_("Number of times lift is triggered before layout is changed")) 
		self.liftEnableCombo.set_tooltip_text(_("Sets whether lift functionality is enabled or not")) 
		self.dateFormatEntry.set_tooltip_text(_("Date format the client should render dates in when displaying RSS tickers")) 
		self.libraryEntry.set_tooltip_text(_("Which folder to store content in. Can be relative or absolute path")) 
		self.socketTimeSpin.set_tooltip_text(_("How long should we wait (in seconds) before timing out a hung socket")) 
		self.checksumCheckButton.set_tooltip_text(_("Should the client checksum all downloaded content to ensure it's unchanged at startup")) 
		self.lowTextureCheckButton.set_tooltip_text(_("Should the client attempt to minimise the amount of graphics texture memory it uses")) 
		self.framesSpin.set_tooltip_text(_("How many fps to force the client to run")) 
		self.vwidthSpin.set_tooltip_text(_("Width of the rendered virtual output screen (this will be a section within the overall window")) 
		self.vheightSpin.set_tooltip_text(_("Height of the rendered virtual output screen (this will be a section within the overall window")) 
		self.vrotateSpin.set_tooltip_text(_("Angle to rotate virtual window within the rendered output window")) 
		self.schedulerCombo.set_tooltip_text(_("Which scheduler module to use")) 
		self.downloaderCombo.set_tooltip_text(_("Which download manager module to use")) 
		self.colourDepthCombo.set_tooltip_text(_("Colour depth of the rendered output")) 

		self.xmdsLicenseKeyEntry.set_tooltip_text(_("Sets license key value to use when syncronising from memory stick"))
#		self.manualUpdateCombo.set_tooltip_text(_("Sets whether update from memory stick is enabled"))

		self.lift8TagText.set_tooltip_text(_("Tag associated with lift input"))
		self.lift9TagText.set_tooltip_text(_("Tag associated with lift input"))
		self.lift10TagText.set_tooltip_text(_("Tag associated with lift input"))
		self.lift11TagText.set_tooltip_text(_("Tag associated with lift input"))
		self.lift12TagText.set_tooltip_text(_("Tag associated with lift input"))
		self.lift13TagText.set_tooltip_text(_("Tag associated with lift input"))
		self.lift14TagText.set_tooltip_text(_("Tag associated with lift input"))
		self.lift15TagText.set_tooltip_text(_("Tag associated with lift input"))

		self.thirdSerialText.set_tooltip_text(_("Third serial port to use for lift purposes"))
		self.fourthSerialText.set_tooltip_text(_("Fourth serial port to use for lift purposes"))

		self.mediaInventoryCombo.set_tooltip_text(_("Set whether media is added to the inventory"))

		self.scanCodeNextText.set_tooltip_text(_("Set a scancode for incrementing the counter"))
		self.scanCodePrevText.set_tooltip_text(_("Set a scancode for decrementing the counter"))

		self.scanCodeResetText.set_tooltip_text(_("Set a scancode to reset the counter"))
		self.counterMaxSpin.set_tooltip_text(_("Set the maximum value for the counter"))

		self.osdBackColourText.set_tooltip_text(_("Set the background colour (RGB)"))
		self.osdBackOpacitySpin.set_tooltip_text(_("Set a value for the pop-up opacity (0-100%)"))
		self.osdFontSizeSpin.set_tooltip_text(_("Set a value for the font size of the counter text in the pop-up"))

		self.osdWidthSpin.set_tooltip_text(_("Set a value for the width of the counter pop-up (0-100%)"))
		self.osdTimeoutSpin.set_tooltip_text(_("Set a value for the counter pop-up timeout (seconds)"))
		self.osdBackColourButton.set_tooltip_text(_("Open a colour chooser to select the background colour"))
		self.osdFontColourButton.set_tooltip_text(_("Open a colour chooser to select the font colour"))

	def getConfValues(self):

		model = self.logTypeCombo.get_model()
		index = self.logTypeCombo.get_active()
#		logTypeText = model[index][0]

		logTypeText = self.logWriterTypes[index]

		#Media inventory combobox	
		mediaInvModel = self.mediaInventoryCombo.get_model()	
		mediaInvIndex = self.mediaInventoryCombo.get_active()
		mediaInvText = mediaInvModel[mediaInvIndex][0]

		configType = "Main"

		serverUrl = [configType,self.serverURLText.get_text()]
		clientId = [configType,self.clientIDText.get_text()]
		serverKey = [configType,self.serverKeyText.get_text()]
		refresh = [configType,int(self.refreshText.get_text())]		
		serverConn = [configType,str(self.serverConnBool.get_active()).lower()]
		fullScreen = [configType,str(self.fullScreenBool.get_active()).lower()]
		screenWidth = [configType, self.screenWidthText.get_value_as_int()]
		screenHeight = [configType, self.screenHeightText.get_value_as_int()]
		captureStats = ["Stats",str(self.captureStatisticsBool.get_active()).lower()]
		queueSize = ["Stats",self.queueSizeText.get_value_as_int()]
		logType = ["Logging", logTypeText]
		logVal = ["Logging",self.logLevelSpin.get_value_as_int()]
		xmdsClientName = ["Main",self.clientNameText.get_text()]
		mediaInventory = ["Main",mediaInvText.lower()]


		self.logger5.info("ServerURL: %s"%serverUrl)
		self.logger5.info("clientID: %s"%clientId)
		self.logger5.info("serverKey: %s"%serverKey)
		self.logger5.info("refresh: %s"%refresh)
		self.logger5.info("serverConn: %s"%serverConn)
		self.logger5.info("fullScreen: %s"%fullScreen)
		self.logger5.info("screenWidth: %s"%screenWidth)
		self.logger5.info("screenHeight: %s"%screenHeight)
		self.logger5.info("captureStats: %s"%captureStats)
		self.logger5.info("queueSize: %s"%queueSize)
		self.logger5.info("logType: %s"%logType)
		self.logger5.info("logVal: %s"%logVal)
		self.logger5.info("xmdsClientName: %s"%xmdsClientName)
		
		#Take the boolean values and make them lower case.

		configOptions = {"xmdsUrl": serverUrl, "xmdsClientID": clientId,"xmdsKey":serverKey,"xmdsUpdateInterval":refresh,"requireXMDS":serverConn,"fullScreen":fullScreen,"width":screenWidth,"height":screenHeight,"collect":captureStats,"queueSize":queueSize,"logWriter":logType,"logLevel":logVal,"xmdsClientName":xmdsClientName,"mediaInventory":mediaInventory}

		#GET THE LIFT OPTIONS
		

		#ONLY DO THIS IF THE LIFT TAB IS SHOWING
		#THEN ADD THEM TO THE DICTIONARY

#		if self.liftTabVisible == True:

		#The above is deprecated. This is because we don't want the information to be
		#"deleted" from the configuration file if we choose not to show these options
		#on subsequent file loads
		if 1:

			configType = "Lift"
			configType1 = "LiftTags"

			model = self.liftEnableCombo.get_model()
			index = self.liftEnableCombo.get_active()
			liftEnableText = model[index][0].lower()

			liftDefaultTag = [configType1,self.liftDefaultTagText.get_text()]
			lift15Tag = [configType1, self.lift15TagText.get_text()]
			lift14Tag = [configType1, self.lift14TagText.get_text()]
			lift13Tag = [configType1, self.lift13TagText.get_text()]
			lift12Tag = [configType1, self.lift12TagText.get_text()]
			lift11Tag = [configType1, self.lift11TagText.get_text()]
			lift10Tag = [configType1, self.lift10TagText.get_text()]
			lift9Tag = [configType1, self.lift9TagText.get_text()]
			lift8Tag = [configType1, self.lift8TagText.get_text()]
			lift7Tag = [configType1, self.lift7TagText.get_text()]
			lift6Tag = [configType1, self.lift6TagText.get_text()]
			lift5Tag = [configType1, self.lift5TagText.get_text()]
			lift4Tag = [configType1, self.lift4TagText.get_text()]
			lift3Tag = [configType1, self.lift3TagText.get_text()]
			lift2Tag = [configType1, self.lift2TagText.get_text()]
			lift1Tag = [configType1, self.lift1TagText.get_text()]
			lift0Tag = [configType1, self.lift0TagText.get_text()]
			firstSerial = [configType, self.firstSerialText.get_text()]
			secondSerial = [configType, self.secondSerialText.get_text()]
			thirdSerial = [configType, self.thirdSerialText.get_text()]
			fourthSerial = [configType, self.fourthSerialText.get_text()]
			liftTrigger = [configType, self.liftTriggerValue.get_text()]
			liftEnable = [configType, liftEnableText]
		
			if liftDefaultTag[1] != "":
				configOptions["default"] = liftDefaultTag

			if lift15Tag[1] != "":
				configOptions["lift15"] =lift15Tag

			if lift14Tag[1] != "":
				configOptions["lift14"] =lift14Tag

			if lift13Tag[1] != "":
				configOptions["lift13"] =lift13Tag

			if lift12Tag[1] != "":
				configOptions["lift12"] =lift12Tag

			if lift11Tag[1] != "":
				configOptions["lift11"] =lift11Tag

			if lift10Tag[1] != "":
				configOptions["lift10"] =lift10Tag

			if lift9Tag[1] != "":
				configOptions["lift9"] =lift9Tag

			if lift8Tag[1] != "":
				configOptions["lift8"] =lift8Tag

			if lift7Tag[1] != "":
				configOptions["lift7"] =lift7Tag

			if lift6Tag[1] != "":
				configOptions["lift6"] =lift6Tag

			if lift5Tag[1] != "":
				configOptions["lift5"] =lift5Tag

			if lift4Tag[1] != "":
				configOptions["lift4"] =lift4Tag

			if lift3Tag[1] != "":
				configOptions["lift3"] =lift3Tag

			if lift2Tag[1] != "":
				configOptions["lift2"] =lift2Tag

			if lift1Tag[1] != "":
				configOptions["lift1"] =lift1Tag
		
			if lift0Tag[1] != "":
				configOptions["lift0"] =lift0Tag

			if firstSerial[1] != "":
				configOptions["serial0"] =firstSerial

			if secondSerial[1] != "":
				configOptions["serial1"] =secondSerial

			if thirdSerial[1] != "":
				configOptions["serial2"] =thirdSerial

			if fourthSerial[1] != "":
				configOptions["serial3"] =fourthSerial


			if liftEnable[1] != "false":
				configOptions["enabled"] =liftEnable

			if liftTrigger != "0":
				configOptions["trigger"] =liftTrigger

#		if self.advancedTabVisible == True:

		#The above is deprecated. This is because we don't want the information to be
		#"deleted" from the configuration file if we choose not to show these options
		#on subsequent file loads
		if 1:
			configType = "Main"

			model = self.schedulerCombo.get_model()
			index = self.schedulerCombo.get_active()
			schedulerComboText = model[index][0]

			model = self.downloaderCombo.get_model()
			index = self.downloaderCombo.get_active()
			downloaderComboText = model[index][0]

			model = self.colourDepthCombo.get_model()
			index = self.colourDepthCombo.get_active()
			colourDepthComboText = model[index][0]

			xmdsLicenseKeyEntry = [configType,self.xmdsLicenseKeyEntry.get_text()]

#			model = self.manualUpdateCombo.get_model()
#			index = self.manualUpdateCombo.get_active()
#			manualUpdateText = model[index][0]

			manualUpdateText = str(self.offlineCheckButton.get_active()).lower()

			manualUpdate = [configType,manualUpdateText.lower()]

			dateFormatEntry = ["TickerMedia", self.dateFormatEntry.get_text()]
		
			libraryEntry = [configType, self.libraryEntry.get_text()]
			socketTimeSpin = [configType, self.socketTimeSpin.get_text()]
			checksum = [configType, str(self.checksumCheckButton.get_active()).lower()]
			lowTexture = [configType, str(self.lowTextureCheckButton.get_active()).lower()]


			frames = [configType, self.framesSpin.get_text()]
			vwidth = [configType, self.vwidthSpin.get_text()]
			vheight = [configType, self.vheightSpin.get_text()]
			vrotate = [configType, self.vrotateSpin.get_text()]
			scheduler = [configType, schedulerComboText]
			downloader = [configType, downloaderComboText]
			colourDepth = [configType, colourDepthComboText]
			
			if xmdsLicenseKeyEntry[1] != "":
				configOptions["xmdsLicenseKey"] = xmdsLicenseKeyEntry

			if manualUpdateText[1] != "":
				configOptions["manualUpdate"] = manualUpdate


			if dateFormatEntry[1] != "":	
				configOptions["dateFormat"] = dateFormatEntry
	
			if libraryEntry[1] != "":
				configOptions["libraryDir"] = libraryEntry
	
			if socketTimeSpin[1] != "0":
				configOptions["socketTimeout"] = socketTimeSpin

			if checksum[1] == "true":
				configOptions["checksumPreviousDownloads"] = checksum

			if lowTexture[1] == "true":
				configOptions["lowTextureMemory"] = lowTexture

			if frames[1] != "0":
				configOptions["fps"] = frames
	
			if vwidth[1] != "0":
				configOptions["vwidth"] = vwidth

			if vheight[1] != "0":
				configOptions["vheight"] = vheight

			if vrotate[1] != "0":
				configOptions["vrotation"] = vrotate

			if scheduler[1] != "":
				configOptions["scheduler"] = scheduler

			if downloader[1] != "":
				configOptions["downloader"] = downloader

			if colourDepth[1] != "":
				configOptions["bpp"] = colourDepth 

		#Now all the counter options

		if 1:
			
			configType = "TicketCounter"

			scanCodePrev = [configType,self.scanCodePrevText.get_text()]
			scanCodeNext = [configType,self.scanCodeNextText.get_text()]
			scanCodeReset = [configType,self.scanCodeResetText.get_text()]
			counterMax = [configType,self.counterMaxSpin.get_text()]

			osdBackColour = [configType,self.osdBackColourText.get_text()]
			osdBackOpacity = [configType,str(self.osdBackOpacitySpin.get_value()/100)]
			osdFontSize = [configType,self.osdFontSizeSpin.get_text()]
			osdWidth = [configType,self.osdWidthSpin.get_text()]
			osdTimeout = [configType,str(int(self.osdTimeoutSpin.get_value()*1000))]
			osdFontColour = [configType,self.osdFontColourText.get_text()]

			if scanCodePrev[1] != "":
				configOptions["prevScanCode"] = scanCodePrev

			if scanCodeNext[1] != "":
				configOptions["nextScanCode"] = scanCodeNext

			if scanCodeReset[1] != "":
				configOptions["resetScanCode"] = scanCodeReset

			if counterMax[1] != "0":
				configOptions["maxCount"] = counterMax

			if osdBackColour != "":
				configOptions["osdBackColour"] = osdBackColour

			if osdBackOpacity != "":
				configOptions["osdBackOpacity"] = osdBackOpacity

			if osdFontSize != "":
				configOptions["osdFontSize"] = osdFontSize

			if osdWidth != "":
				configOptions["osdWidthPercent"] = osdWidth

			if osdTimeout != "":
				configOptions["osdTimeOut"] = osdTimeout

			if osdFontColour != "":
				configOptions["osdFontColour"] = osdFontColour


		return configOptions
def cmdOptions():
	options = sys.argv[1:]
	
	#For each option in the array strip off any - characters and convert to lower case
	
	for i in range(len(options)):
		options[i] = options[i].strip("-").lower()

	return options

if __name__ == "__main__":

	#Grab the command line options
	options = cmdOptions()
	
	#Find out if the lift option has been passed
	lift = False
	try:
		options.index("lift")
		lift = True
	except ValueError:
		print "Option not found"
		lift = False


	wine = xiboConfWindow("client.conf", lift = lift)
	gtk.main()
