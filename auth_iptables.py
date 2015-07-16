import paho.mqtt.client as paho
from config import mqtt_topic, mqtt_broker
import re
import subprocess

re_mac = re.compile(r'^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$')
broker_ip = '127.0.0.1'
mac_file = '/proc/net/arp'
command_base = '/usr/bin/sudo /usr/sbin/iptables -t mangle %s internet -m mac --mac-source %s -j RETURN'

class AuthIPTables:
	arp_table = {}

	def allow(self, ip):
		try:
			mac = self.arp_table[ip]
		except KeyError:
			mac = self._get_mac(ip)
		if mac:
			self._exec(command_base%('-I', mac))
		return mac

	def deny(self, mac):
		self._exec(command_base%('-D', mac))

	def _get_mac(self, ip):
		result = None
		mf = open(mac_file, 'r')
		for line in mf.readlines():
			res = line.split()
			if res[0] == ip and re_mac.match(res[3]):
				result = res[3]
				self.arp_table[ip] = res[3]
		mf.close()
		return result

	def _exec(self, command):
		subprocess.Popen(command.split())
