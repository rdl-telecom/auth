#!/usr/bin/env python

from config import session_time
import time
import threading
from auth_icomera import AuthIcomera

locker = threading.Lock()
authorized = []

class Scheduler (threading.Thread):
	def __init__(self, ip):
		locker.acquire()
		is_authorized = ip in authorized
		locker.release()
		if is_authorized:
			raise ValueError('Already authorized')
		threading.Thread.__init__(self)
		self.duration = session_time
		self.ip = ip
		self.auth = AuthIcomera()
		self.setDaemon(True)
		if self.auth.allow(self.ip):
			self.start()
			authorized.append(self.ip)
		else:
			raise ValueError('Authorization error')

	def run(self):
		time.sleep(self.duration)
		self.auth.deny(self.ip)
		locker.acquire()
		authorized.remove(self.ip)
		locker.release()
