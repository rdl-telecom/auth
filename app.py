#!/usr/bin/env python

from config import session_time
import web
import urllib2
import logging
import logging.handlers
import socket
from scheduler import Scheduler

log_file = '/tmp/auth.log'
log_max_size = 1048576
log_num_rotates = 1

logger = logging.getLogger('user.auth')
logger.setLevel(logging.DEBUG)
fh = logging.handlers.RotatingFileHandler(log_file, maxBytes=log_max_size, backupCount=log_num_rotates)
fh.setLevel(logging.DEBUG)
fmt = logging.Formatter('%(asctime)s %(name)-16s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
fh.setFormatter(fmt)
logger.addHandler(fh)

urls = (
	'/auth.html?', 'auth'
)

class auth:
	def GET(self):
		req = web.input()
		try:
			success_url = urllib2.unquote(req['success'])
			error_url = urllib2.unquote(req['error'])
		except Exception as e:
			return web.badrequest()
		print success_url
		xff = web.ctx.env.get('HTTP_X_FORWARDED_FOR', None)
		if not xff:
			xff = web.ctx.env.get('HTTP_REMOTE_ADDR', None)
			if not xff:
				logger.error('Cannot determine user IP address')
				return web.badrequest()
		ip = xff.split(',')[0].strip()
		result = success_url
		try:
			logger.info('Accepting user {0}'.format(ip))
			scheduler = Scheduler(ip)
		except AssertionError:
			pass
		except ValueError as e:
			result = error_url
			logger.error('Cannot authenticate user {0}. Cause "{1}"'.format(ip, e))
		raise web.seeother(result)

app = web.application(urls, globals())

if __name__ == '__main__':
	app.run()
