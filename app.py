#!/usr/bin/env python

from config import session_time, adv_time
import web
import logging
import logging.handlers
import socket
import urllib2
from scheduler import Scheduler
import memcache

redirect_base_url = 'http://aero.rdl.club/useragreement.html'

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

mcache = memcache.Client(['127.0.0.1:11211'])
scheduler = Scheduler()

injection_js = '/www-main/portal/assets/js/afrsasync.js'

urls = (
	'/', 'index',
	'/auth.html?', 'auth',
	'/assets/js/afrsasync.js', 'injection'
)

class network_authentication_required(web.HTTPError):
	def __init__(self, location):
		status = "511 Network Authentication Required"
		headers = {
			'Content-Type' : 'text/html; charset=utf-8',
			'Location' : location,
			'Expires' : '-1',
			'Pragma' : 'no-cache',
			'Cache-Control' : 'no-cache,max-age=0,no-store'
		}
		data = '''<html>
	<head>
		<title>Network Authentication Required</title>
		<meta http-equiv="refresh" content="0; url={0}">
	</head>
	<body>
	</body>
</html>'''.format(location)
		web.HTTPError.__init__(self, status, headers, data)

class index:
	def GET(self):
		xff = web.ctx.env.get('HTTP_X_FORWARDED_FOR', None)
		if not xff:
			xff = web.ctx.env.get('HTTP_REMOTE_ADDR', None)
			if not xff:
				logger.error('Cannot determine user IP address')
				return web.badrequest()
		ip = xff.split(',')[0].strip()

		query_string = web.ctx.env.get('QUERY_STRING', '')
		if not query_string:
			query_string = web.ctx.env.get('HTTP_REFERER', 'http://yandex.ru')

		if ip in scheduler._authorized:
			raise web.redirect(query_string)

		redirect_url = '?'.join((redirect_base_url, urllib2.quote(query_string)))
		raise network_authentication_required(redirect_url)

class injection:
	def GET(self):
		web.header('Content-type', 'application/x-javascript; charset=utf-8')
		web.header('Pragma', 'no-cache')
		web.header('Expires', '0')
		web.header('Cache-Control', 'no-cache,max-age=0,no-store')
		ip = web.ctx.env.get('HTTP_X_REAL_IP', None)
		resp = ''
		if ip:
			client = mcache.get(ip)
			if not client:
				mcache.set(ip, 'active', adv_time)
				resp = mcache.get(injection_js)
				if not resp:
					f = open(injection_js, 'r')
					resp = f.read()
					f.close()
					mcache.set(injection_js, resp)
		print resp
		return resp

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
		result = '/auth_ok.html?url=' + urllib2.unquote(req['success'])
		try:
			logger.info('Accepting user {0}'.format(ip))
			scheduler.authorize(ip)
		except AssertionError:
			pass
		except ValueError as e:
			result = urllib2.unquote(req['error'])
			logger.error('Cannot authenticate user {0}. Cause "{1}"'.format(ip, e))
		raise web.seeother(result)

app = web.application(urls, globals())

if __name__ == '__main__':
	app.run()
