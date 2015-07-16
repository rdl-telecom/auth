#!/usr/bin/env python

import paho.mqtt.client as paho
from config import mqtt_topic
import subprocess
import time

broker_ip = '127.0.0.1'
command_map = { 'enable' : '-I', 'disable' : '-D' }
command_base = '/usr/sbin/iptables -t mangle %s internet -m mac --mac-source %s -j RETURN'

class Listener:
	is_connected = False
	def __init__(self):
		self.client = paho.Client()
		self.client.on_connect = self._on_connect
		self.client.on_disconnect = self._on_disconnect
		self.client.on_message = self._on_message
		self._connect()

	def run(self):
		try:
			self.client.loop_forever(timeout=0.1, retry_first_connection=True)
		except KeyboardInterrupt:
			pass
		except Exception as e:
			print e

	def __del__(self):
		if self.is_connected:
			self.client.disconnect()

	def _connect(self):
		if not self.is_connected:
			try:
				self.client.connect(broker_ip, keepalive=60)
			except Exception as e:
				print e
				pass

	def _on_connect(self, client, userdata, flags, rc):
		print 'connected'
		self.is_connected = True
		self.client.subscribe(mqtt_topic)

	def _on_disconnect(self, client, userdata, rc):
		print 'disconnected'
		self.is_connected = False
		self._connect()

	def _on_message(self, client, userdata, msg):
		print msg.payload
		command, mac = msg.payload.split()
		self._exec(command_base%(command_map[command], mac))

	def _exec(self, command):
		print command
		subprocess.Popen(command.split())

if __name__ == '__main__':
	listener = Listener()
	listener.run()
