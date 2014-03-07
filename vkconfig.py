#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

config_filename = 'vkconfig.txt'
config = open(config_filename, 'r')

def read():
	global config
	while True:
		l = config.readline().strip()
		if l=='': continue
		try:
			l = l.substr(0, l.index('#'))
			l=l.strip()
		except: pass
		print l
		if l!='': return l
		

LOGIN = read()
PASS = read()
APPID = '3715935'

#Разрешить дополнительные функции (проставить лайки в автом. режиме, например)
EXTRA_FUNC = read()

#Работа через промежуточный сервер.
USE_API_RELAY = 1
RELAY_ADDR = 'startapp.mooo.com'
RELAY_PORT = 30047

USE_PNM = read()
PNM_TEMP = os.getcwd()+'/pnm/'
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

OPEN_XDG = 1
OPEN_WIN_OSSF = 0
OPEN_TMPDIR = os.path.join(os.getcwd(), 'opentmp', '')

DEBUG=1

#make tmp dirs
try: os.mkdir(OPEN_TMPDIR)
except: pass
try: os.mkdir(PNM_TEMP)
except: pass
