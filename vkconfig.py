#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import sys
reload(sys)
sys.setdefaultencoding('utf8')

CSD=os.path.split(os.path.realpath(sys.argv[0]))[0]
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
		if l!='': return l
		

LOGIN = read()
PASS = read()
APPID = '3715935'

USE_PNM = int(read()) #Конвертация в Portable Anymap перед показом. В частности для совместимости с WinCE.
PNM_TEMP = os.path.join(CSD, 'pnm', '')
#PNM_TEMP = '\\Storage Card\\PNM\\' #Для WinCE - полные пути.
#Максимальна ширина окна профиля если без фото.
INFO_MAX_WIDTH=350
SHOW_IMAGES = 1
PROFILE_PHOTO = 'photo_max'

PHOTOLIST_ROWS = 3
PHOTOLIST_COLS = 3
PHOTOLIST_SIZE = 'src'
SAVE_SIZES = { 1: 'src_big', 2: 'src_xbig', 3: 'src_xxbig'}

#Разрешить дополнительные функции (проставить лайки в автом. режиме, например)
EXTRA_FUNC = int(read())

#Работа через промежуточный сервер.
USE_API_RELAY = 0
RELAY_ADDR = 'startapp.mooo.com'
RELAY_PORT = 30047

OPEN_XDG = 0
OPEN_OSSF = 0
OPEN_METHOD = read()
OPEN_TMPDIR = os.path.join(CSD, 'opentmp', '')

TIME_FORMAT = '%d.%m.%y %H:%M'

MESSAGE_NOTIFY = read()

MESSAGE_PROBE_INTERVAL = float(read())

DEBUG=1

#make tmp dirs
try: os.mkdir(OPEN_TMPDIR)
except: pass
try: os.mkdir(PNM_TEMP)
except: pass
