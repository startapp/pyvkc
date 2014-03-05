#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vkconfig
MY_ADDR=('', vkconfig.RELAY_PORT)
vkconfig.USE_API_RELAY=0 #Я сам промежуток.
import vkontakte
import socket
import vk_auth
from vkontakte.api import json
from threading import Thread

def session(sock, addr):
	sock.send("Vk API RELAY at startapp's home by startapp; DN\n")
	print 'Connected: '+str(addr)
	cf = sock.makefile()
	while 1:
		c = cf.readline().strip()
		if c == 'LOG1':
			logstr = cf.readline().strip()
			uid, passwd, appid = logstr.split(' ')
			scope = cf.readline().strip()+',nohttps'
			token, uid, secret = vk_auth.auth(uid, passwd, appid, scope)
			cf.write('%s\n'%(' '.join((token, uid, secret))))
			cf.flush()
			vk_api = vkontakte.API(token=token, api_secret=secret)
		elif c == 'REQE':
			method = cf.readline().strip()
			cf.write('OK\n')
			cf.flush()
			kwargs = {}
			while 1:
				c2 = cf.readline().strip()
				if c2 == 'PARA':
					key = cf.readline().strip()
					leng = int(cf.readline().strip())
					value = cf.read(leng).strip()
					kwargs[key]=value
				elif c2 == 'ENDP':
					kwargs['method']=method
					resp = json.dumps(vk_api.__call__(**kwargs))
					cf.write('ANSW\n')
					cf.write('%d\n'%len(resp))
					cf.write(resp)
					cf.flush()
					break
		elif c == 'QUIT':
				sock.close()
				return
	sock.close()

sock = socket.socket()
sock.bind(MY_ADDR)
sock.listen(0)
while True:
	s,c = sock.accept()
	Thread(target = session, args=(s,c)).start()

