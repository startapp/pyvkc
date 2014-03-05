#!/usr/bin/env python
# -*- coding: utf-8 -*-

LOGIN = ''
PASS = ''
APPID = '3715935'

#Работа через промежуточный сервер.
USE_API_RELAY = 1
RELAY_ADDR = 'startapp.mooo.com'
RELAY_PORT = 30047

SHOW_IMAGES = 1
PROFILE_PHOTO = 'photo_max'
#Конвертация в PNM перед показом. В частности для совместимости с WinCE.
USE_PNM = 1
PNM_TEMP = '.pnm/'
#PNM_TEMP = '\\Storage Card\\PNM\\' #Для WinCE - полные пути.
#Максимальна ширина окна профиля если без фото.
INFO_MAX_WIDTH=350

DEBUG=1
