#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

CSD=os.path.split(os.path.realpath(sys.argv[0]))[0]
print 'Config: ', CSD
config_filename = os.path.join(CSD, 'vkconfig.txt')
config = open(config_filename, 'r')

def read():
	global config
	while True:
		l = config.readline().strip()
		if l=='': continue
		try:
			l = l[0:l.index('#')]
			l=l.strip()
		except: pass
		print repr(l)
		if l!='': return l
		

LOGIN = read()
PASS = read()
APPID = '3715935'

USE_PNM = int(read())
PNM_TEMP = os.path.join(CSD, 'pnm', '')
#PNM_TEMP = '\\Storage Card\\PNM\\' #Для WinCE - полные пути.
#Максимальна ширина окна профиля если без фото.
INFO_MAX_WIDTH=350
SHOW_IMAGES = 1
PROFILE_PHOTO = 'photo_max'
#Конвертация в Portable Anymap перед показом. В частности для совместимости с WinCE.

PHOTOLIST_ROWS = 3
PHOTOLIST_COLS = 3
PHOTOLIST_SIZE = 'src'
SAVE_SIZE = 'src_big'

#Разрешить дополнительные функции (проставить лайки в автом. режиме, например)
EXTRA_FUNC = int(read())

#Работа через промежуточный сервер.
USE_API_RELAY = 0
RELAY_ADDR = 'startapp.mooo.com'
RELAY_PORT = 30047

OPEN_XDG = 0
OPEN_OSSF = 0
OPEN_METHOD = read()
print 'OM=', repr(OPEN_METHOD)
OPEN_TMPDIR = os.path.join(CSD, 'opentmp', '')

TIME_FORMAT = '%d.%m.%y %H:%M'

DEBUG=1

#make tmp dirs
try: os.mkdir(OPEN_TMPDIR)
except: pass
try: os.mkdir(PNM_TEMP)
except: pass
