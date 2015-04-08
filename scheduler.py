#!/usr/bin/env python

from config import session_time
import time
import threading
from auth_icomera import AuthIcomera

class Scheduler (threading.Thread):
	def __init__(self, ip):
		threading.Thread.__init__(self)
		self.duration = session_time
		self.ip = ip
		self.auth = AuthIcomera()
		self.setDaemon(True)
		if self.auth.allow(self.ip):
			self.start()
		else:
			raise Exception

	def run(self):
		print 'hello!'
		time.sleep(self.duration)
		print 'slept'
		self.auth.deny(self.ip)
