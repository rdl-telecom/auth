import paho.mqtt.client as paho
from config import mqtt_topic, mqtt_broker
import re

re_mac = re.compile(r'^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$')
broker_ip = '127.0.0.1'
mac_file = '/proc/net/arp'


class AuthMQTT:
	arp_table = {}
	is_connected = False
	def __init__(self):
		self.client = paho.Client('captive')
		self.client.on_disconnect = self._on_disconnect
		self._connect()

	def __del__(self):
		if self.is_connected:
			self.client.disconnect()

	def _connect(self):
		if not self.is_connected:
			try:
				self.client.connect(mqtt_broker, keepalive=60)
				self.is_connected = True
				print 'connected'
			except Exception as e:
				print e
				pass

	def allow(self, ip):
		print 'allow ' + ip
		result = None
		try:
			mac = self.arp_table[ip]
		except KeyError:
			mac = self._get_mac(ip)
		print 'mac = ' + mac
		print self.arp_table
		if mac and self._publish(' '.join(('enable', mac))):
			result = self.arp_table[ip] = mac
		return result

	def deny(self, mac):
		print 'deny ' + mac
		return self._publish(' '.join(('disable', mac)))

	def _on_disconnect(self, client, userdata, rc):
		print 'disconnected'
		self.is_connected = False
		self._connect()

	def _publish(self, command):
		print 'publish ' + command
		result = False
		self._connect()
		if self.is_connected:
			try:
				self.client.publish(mqtt_topic, command)
				result = True
				print 'publish success'
			except Exception as e:
				print e
				pass
		return result

	def _get_mac(self, ip):
		result = None
		mf = open(mac_file, 'r')
		for line in mf.readlines():
			res = line.split()
			if res[0] == ip and re_mac.match(res[3]):
				result = res[3]
		mf.close()
		return result
