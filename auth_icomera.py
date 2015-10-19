from config import auth_info
import paramiko
import re

re_mac = re.compile(r'^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$')

class AuthIcomera:
	command_add = 'hotcli add %s %s'
	command_allow = 'hotcli allow %s'
	command_deny = 'hotcli deny %s'
	command_get_mac = 'cat /proc/net/arp | grep %s | cut -b 42-58'
	result_allow_ok = 'allow OK'
	result_deny_ok = 'deny OK'

	def __init__(self):
		self.credentials = auth_info
		self.ssh = paramiko.SSHClient()
		self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.connect()

	def connected():
		transport = self._ssh.get_transport() if self._ssh else None
		return transport and transport.is_active()

	def connect(self):
		counter = 10
		while not self.connected():
			try:
				self.ssh.connect(hostname = self.credentials['host'], username = self.credentials['username'],
						password = self.credentials['password'], port = self.credentials['port'], timeout = 3)
			except:
				pass
			counter -= 1
			if counter == 0:
				break

	def disconnect(self):
		self.ssh.close()

	def allow(self, ip):
		result = False
		self.connect()
		if self.connected():
			mac = self.get_mac(ip)
			if mac:
				self.command(self.command_add%(ip, mac))
			if (self.command(self.command_allow%ip) == self.result_allow_ok):
				result = True
		return result

	def deny(self, ip):
		result = False
		self.connect()
		if self.connected and self.command(self.command_deny%ip) == self.result_deny_ok:
			result = True
		return result

	def command(self, command):
		stdin, stdout, stderr = self.ssh.exec_command(command)
		return stdout.read()[:-1]

	def get_mac(self, ip):
		mac = self.command(self.command_get_mac%ip)
		if not re_mac.match(mac):
			return None
		return mac
