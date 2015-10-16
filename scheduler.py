#!/usr/bin/env python

from config import session_time
import time
from threading import Thread, Lock
from auth_icomera import AuthIcomera

class IPList:
	_list = []
	_lock = Lock()

	def add(self, ip):
		self._lock.acquire()
		self._list.append(ip)
		self._lock.release()

	def delete(self, ip):
		self._lock.acquire()
		self._list.remove(ip)
		self._lock.release()
	
	def __contains__(self, ip):
		return ip in self._list

class Scheduler:
	_authorized = IPList()

	def __init__(self):
		self.auth = AuthIcomera()

	def authorize(self, ip):
		if ip in self._authorized:
			raise AssertionError('Already authorized')
		mac = self.auth.allow(ip)
		if mac:
			task_thread = Thread(name=mac, target=self.task, args=(ip, mac))
			task_thread.daemon = True
			task_thread.start()
		else:
			raise ValueError('Authorization error')

	def task(self, ip, mac):
		self._authorized.add(ip)
		time.sleep(session_time)
		self.auth.deny(ip)
		self._authorized.delete(ip)
