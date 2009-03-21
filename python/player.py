#!/usr/bin/python
# -*- coding: utf-8 -*-

from libavg import avg, anim
import time, Queue

eventQueue = Queue.Queue(0)
eventQueue.put(1)

Player = avg.Player()


Player.loadFile("assets/player.avg")



def nextStep():
	step = eventQueue.get()
	if step == 1:
		bg = Player.getElementByID("bg")
		region1 = Player.createNode('<div id="region1" x="30" y="30" width="300" height="30" opacity="1"><words id="ClashText" x="" y="" font="arial" text="Should I stay or should I go?" /></div>')
		bg.appendChild(region1)
		eventQueue.put(2)
	elif step == 2:
		bg = Player.getElementByID("bg")
		bg.removeChild(0)
		eventQueue.put(3)
	elif step == 3:
		bg = Player.getElementByID("bg")
		region1 = Player.createNode('<div id="region1" x="30" y="30" width="300" height="30" opacity="1"><words id="ClashText" x="" y="" font="arial" text="Should I go or should I stay?" /></div>')
		bg.appendChild(region1)
		eventQueue.put(4)
	elif step == 4:
		bg = Player.getElementByID("bg")
		bg.removeChild(0)
		eventQueue.put(1)

Player.setInterval(1000, nextStep)
Player.play()
