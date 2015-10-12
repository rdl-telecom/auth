#!/usr/bin/env python

from config import session_time, log_size, log_rotates
import web
import logging
import logging.handlers
import socket
import urllib2
from scheduler import Scheduler

redirect_base_url = 'http://aero.rdl.club/useragreement.html'

log_file = '/tmp/auth.log'
log_max_size = log_size
log_num_rotates = log_rotates

logger = logging.getLogger('user.auth')
logger.setLevel(logging.DEBUG)
fh = logging.handlers.RotatingFileHandler(log_file, maxBytes=log_max_size, backupCount=log_num_rotates)
fh.setLevel(logging.DEBUG)
fmt = logging.Formatter('%(asctime)s %(name)-16s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
fh.setFormatter(fmt)
logger.addHandler(fh)

scheduler = Scheduler()

urls = (
	'/allow', 'auth',
)

class auth:
	def GET(self):
		logger.debug('Authentication called')
		req = web.input()
		xff = web.ctx.env.get('HTTP_X_FORWARDED_FOR', None)
		if not xff:
			xff = web.ctx.env.get('HTTP_REMOTE_ADDR', None)
			if not xff:
				logger.error('Cannot determine user IP address')
				return web.badrequest()
		ip = xff.split(',')[0].strip()
		result = '/success.html'
		try:
			logger.info('Accepting user {0}'.format(ip))
			scheduler.authorize(ip)
		except AssertionError:
			pass
		except ValueError as e:
			result = '/'
			logger.error('Cannot authenticate user {0}. Cause "{1}"'.format(ip, e))
		raise web.seeother(result)

app = web.application(urls, globals())

if __name__ == '__main__':
	app.run()
