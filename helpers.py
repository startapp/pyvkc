#!/usr/bin/python
# -*- coding: utf-8 -*-

class TkFilePicker:
	def __init__(self):
		self.tkFileDialog = __import__('tkFileDialog')
	def save_one(self, title=None, fn=''):
		return self.tkFileDialog.asksaveasfilename(title=title, initialfile=fn)

class BuiltinDManager:
	def __init__(self):
		self.urllib2=__import__('urllib2')
	def down_file(self, url):
		fn = FPICKER.save_one('Скачать', fn=self.urllib2.posixpath.basename(url))
		u = self.urllib2.urlopen(url)
		f = open(fn, 'wb')
		f.write(u.read())
		f.close()
		u.close()
		return 1

FPICKER = TkFilePicker()
DM = BuiltinDManager()

