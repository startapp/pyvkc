#!/usr/bin/env python
# -*- coding: utf-8 -*-

LOGIN = ''
PASS = ''
APPID = '3715935'

#Работа через промежуточный сервер.
USE_API_RELAY = 1
RELAY_ADDR = 'startappp.mooo.com'
RELAY_PORT = 30047

SHOW_IMAGES = 1
PROFILE_PHOTO = 'photo_max'
#Конвертация в Portable Anymap перед показом. В частности для 
совместимости с WinCE.
USE_PNM = 1
PNM_TEMP = '.pnm/'
#PNM_TEMP = '\\Storage Card\\PNM\\' #Для WinCE - полные пути.
#Максимальная ширина окна профиля если без фото.
INFO_MAX_WIDTH=350

PHOTOLIST_ROWS = 3
PHOTOLIST_COLS = 3
PHOTOLIST_SIZE = 'src'
SAVE_SIZE = 'src_big'

#Разрешить дополнительные функции (проставить лайки в автом. режиме, например)
EXTRA_FUNC = 1

DEBUG=1
