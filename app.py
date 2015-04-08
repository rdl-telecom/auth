#!/usr/bin/env python

from config import session_time
import web
import logging
import socket
from scheduler import Scheduler

log_file = '/tmp/auth.log'
arp_file = '/proc/net/arp'
ua_file = '/srv/log/user_agents'

logger = logging.getLogger('user.auth')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(log_file)
fh.setLevel(logging.DEBUG)
fmt = logging.Formatter('%(asctime)s %(name)-20s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
fh.setFormatter(fmt)
logger.addHandler(fh)

urls = (
	'/auth.html?', 'auth'
)

class auth:
	def GET(self):
		print web.ctx.env
		req = web.input()
		if not ( 'success' and 'error' in req ):
			return web.badrequest()
		from pprint import pprint
		xff = web.ctx.env.get('HTTP_X_FORWARDED_FOR', None)
		if not xff:
			logger.error('Cannot determine user IP address')
			return web.badrequest()
		ip = xff.split(',')[0].strip()
		result = req['success']
		try:
			logger.info('Accepting user {0}'.format(ip))
			scheduler = Scheduler(ip)
		except:
			logger.error('Cannot authenticate user {0}'.format(ip))
			result = req['error']
		raise web.seeother(result)

class email:
	def POST(self):
		return 200
		
app = web.application(urls, globals())

if __name__ == '__main__':
	app.run()
