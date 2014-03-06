#!/usr/bin/python
# -*- coding: utf-8 -*-

from vkconfig import *
import urllib2
import os
import tkFileDialog

class TkFilePicker:
	def __init__(self):
		pass
	def save_one(self, title=None, fn=''):
		return tkFileDialog.asksaveasfilename(title=title, initialfile=fn)
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
	if OPEN_XDG:
		os.system('xdg-open "%s"'%fn)
	elif OPEN_WIN_OSSF:
		os.startfile(fn)


FPICKER = TkFilePicker()
DM = BuiltinDManager()

