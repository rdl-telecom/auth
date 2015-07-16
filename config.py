#!/usr/bin/env python

import re

value_re = re.compile(r'^.*=\s*([^\s\t]*)\s*$')

config_file = '/srv/config'
users_file = '/srv/users'

mqtt_broker = '127.0.0.1'
mqtt_topic = 'captive/command'

multipliers = { 's' : 1,
		'm' : 60,
		'h' : 3600,
		'd' : 86400
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
		if tail in multipliers.keys():
			seconds = int(s_tm[:-1]) * multipliers[tail]
		else:
			seconds = default
	return seconds

session_time = get_time('SESSION_TIME')
adv_time = get_time('ADV_TIME')
auth_info = {
	'host' : get_config_value('AUTH_HOST'),
	'port' : int(get_config_value('AUTH_PORT')),
	'username' : get_config_value('AUTH_USER'),
	'password' : get_config_value('AUTH_PASS')
}
