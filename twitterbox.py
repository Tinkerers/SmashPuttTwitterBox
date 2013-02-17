#!/usr/bin/python

from settings import *
try:
	import RPi.GPIO as GPIO
	PI = True
except ImportError:
	PI = False

import logging
import Queue
import time
import os
from watcher import Watcher
from printer import Printer
import sys
import traceback
try:
	DEBUG = bool(int(os.environ['DEBUG']))
except KeyError
	DEBUG = False

def main():
	# Setup Logging
	logger = logging.getLogger('twitterbox')
	hdlr = logging.FileHandler(LOG)
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	hdlr.setFormatter(formatter)
	logger.addHandler(hdlr) 

	hdlr = logging.StreamHandler(sys.stdout)
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	hdlr.setFormatter(formatter)
	logger.addHandler(hdlr) 
	if DEBUG:
		logger.setLevel(logging.DEBUG)
	else:
		logger.setLevel(logging.INFO)
	logger.info("Starting up...")

	if PI:
		# Not interested
		GPIO.setwarnings(False)

		# Setup the LCD display
		GPIO.setmode(GPIO.BCM)	     # Use BCM GPIO numbers
		GPIO.setup(LCD_E, GPIO.OUT)  # E
		GPIO.setup(LCD_RS, GPIO.OUT) # RS
		GPIO.setup(LCD_D4, GPIO.OUT) # DB4
		GPIO.setup(LCD_D5, GPIO.OUT) # DB5
		GPIO.setup(LCD_D6, GPIO.OUT) # DB6
		GPIO.setup(LCD_D7, GPIO.OUT) # DB7

		# Setup the alert light
		GPIO.setup(LIGHT_PIN, GPIO.OUT) 
		GPIO.output(LIGHT_PIN, GPIO.LOW)


	# The queue is where messages go to be displayed
	queue = Queue.PriorityQueue()
	
	watcher = None
	printer = None
	loops = 0
	while True:
		try:
			loops = loops + 1
			logger.debug("Main Loop " + str(loops))

			# Make sure our twitter thread is alive and happy
			if not watcher or not watcher.is_alive():
				logger.info("Starting watcher thread")
				watcher = Watcher(queue, logger)
				watcher.setDaemon(True)
				watcher.start()

			# Make sure our printing thread is alive and happy
			if not printer or not printer.is_alive():
				logger.info("Starting printer thread")
				printer = Printer(queue, logger, PI)
				printer.setDaemon(True)
				printer.start()

			# Throw some info in the queue if it's getting low
			if queue.qsize() == 0:
				for w in track:
					queue.put((PRIORITY_LOW, "Watching for:", w, False))
				user_data = watcher.getUserData()
				for k,v in user_data.iteritems():
					queue.put((PRIORITY_LOW, k, v, False))
		except Exception as e:
			logger.error("Exception in main thread: " + str(e))
			traceback.print_tb(sys.exc_info()[2])

		time.sleep(15)

	logger.warn("Exiting main thread")


if __name__ == '__main__':
	main()
