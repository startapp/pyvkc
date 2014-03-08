#!/usr/bin/python
# -*- coding: utf-8 -*-

from vkconfig import *
import urllib2, urlparse
import os
import tkFileDialog
from vkontakte.api import json
import codecs
import requests as r

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'


class TkFilePicker:
	def __init__(self):
		pass
	def save_one(self, title=None, fn=''):
		return tkFileDialog.asksaveasfilename(title=title, initialfile=fn)
	def open_file(self, title=None):
		return tkFileDialog.askopenfilename(title=title)
	def choose_dir(self, title=None):
		return tkFileDialog.askdirectory(title=title)

class BuiltinDManager:
	def __init__(self):
		pass
	def down(self, url, fn):
		u = urllib2.urlopen(url)
		f = open(fn, 'wb')
		f.write(u.read())
		f.close()
		u.close()
	def down_file(self, url):
		fn = FPICKER.save_one('Скачать', fn=urllib2.posixpath.basename(url))
		self.down(url, fn)
		return fn
	def down_dir(self, urls, statusCb=None):
		fn = FPICKER.choose_dir(title='Скачать')
		for i in xrange(len(urls)):
			if statusCb: statusCb(i)
			url = urls[i]
			self.down(url, fn+'/'+urllib2.posixpath.basename(url))
	def open_user(self, url, ft='std'):
		fn = OPEN_TMPDIR+urllib2.posixpath.basename(url)
		DM.down(url, fn)
		open_user(fn)

def open_user(fn):
	print fn
	if OPEN_METHOD=='xdg':
		os.system('xdg-open "%s"'%fn)
	elif OPEN_METHOD=='ossf':
		os.startfile(fn)
	else:
		print 'NOTOPEN'

def upload(url, ff, fn):
	f=open(fn, 'rb')
	urlparts = urlparse.urlsplit(url)
	print urlparts
	data = []
	__data = urlparts[3]
	print __data
	_data = __data.split('&')
	print _data
	for _d in _data:
		_k, _v = _d.split('=')
		print _k, ' =', _v
		data.append((_k, _v))
	res = r.post(urlparts[0]+'://'+urlparts[1]+'/'+urlparts[2], data, files={ff: (fn, f)}).text
	print res
	return res

FPICKER = TkFilePicker()
DM = BuiltinDManager()

