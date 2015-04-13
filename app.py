#!/usr/bin/env python

from config import session_time
import web
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
		if not ( 'success' and 'error' in req ):
			return web.badrequest()
		xff = web.ctx.env.get('HTTP_X_FORWARDED_FOR', None)
		if not xff:
			xff = web.ctx.env.get('HTTP_REMOTE_ADDR', None)
			if not xff:
				logger.error('Cannot determine user IP address')
				return web.badrequest()
		ip = xff.split(',')[0].strip()
		result = req['success']
		try:
			logger.info('Accepting user {0}'.format(ip))
			scheduler = Scheduler(ip)
		except Exception as e:
			logger.error('Cannot authenticate user {0}. Cause "{1}"'.format(ip, e))
			result = req['error']
		raise web.seeother(result)

app = web.application(urls, globals())

if __name__ == '__main__':
	app.run()
