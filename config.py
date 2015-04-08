#!/usr/bin/env python

import re

value_re = re.compile(r'^.*=\s*([^\s\t]*)\s*$')

config_file = '/srv/config'
users_file = '/srv/users'

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

def get_session_time(default=0):
	s_tm = get_config_value('SESSION_TIME')
	try:
		seconds = int(s_tm)
	except ValueError:
		tail = s_tm[-1].lower()
		if tail in multipliers.keys():
			seconds = int(s_tm[:-1]) * multipliers[tail]
		else:
			seconds = default
	return seconds

session_time = get_session_time()
auth_info = {
	'host' : get_config_value('AUTH_HOST'),
	'port' : int(get_config_value('AUTH_PORT')),
	'username' : get_config_value('AUTH_USER'),
	'password' : get_config_value('AUTH_PASS')
}
