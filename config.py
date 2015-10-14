#!/usr/bin/env python

import re

value_re = re.compile(r'^.*=\s*([^\s\t]*)\s*$')

config_file = '/auth/config'
users_file = '/auth/users'

mqtt_broker = '127.0.0.1'
mqtt_topic = 'captive/command'

time_multipliers = {
	's' : 1,
	'm' : 60,
	'h' : 3600,
	'd' : 86400
}

size_multipliers = {
	'b' : 1,
	'k' : 1024,
	'm' : 1048576,
	'g' : 1073741824
}

def get_config_value(param):
	f = open(config_file, 'r')
	buf = f.readlines()
	f.close()
	result = None
	for line in buf:
		if param in line:
			result = value_re.sub('\\1', line)
			break
	return result

def get_time(value ,default=0):
	s_tm = get_config_value(value)
	try:
		seconds = int(s_tm)
	except ValueError:
		tail = s_tm[-1].lower()
		if tail in time_multipliers.keys():
			seconds = int(s_tm[:-1]) * time_multipliers[tail]
		else:
			seconds = default
	return seconds

def get_size(value, default=0):
	s_sz = get_config_value(value)
	try:
		size = int(s_sz)
	except ValueError:
		tail = s_sz[-1].lower()
		if tail in size_multipliers.keys():
			size = int(s_sz[:-1]) * size_multipliers[tail]
		else:
			size = default
	return size

session_time = get_time('SESSION_TIME')

log_size = get_size('LOG_SIZE')
log_rotates = int(get_config_value('LOG_ROTATES')) or 1

auth_info = {
	'host' : get_config_value('AUTH_HOST'),
	'port' : int(get_config_value('AUTH_PORT')),
	'username' : get_config_value('AUTH_USER'),
	'password' : get_config_value('AUTH_PASS')
}
