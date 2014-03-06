#!/usr/bin/python
# -*- coding: utf-8 -*-

class TkFilePicker:
	def __init__(self):
		self.tkFileDialog = __import__('tkFileDialog')
	def save_one(self, title=None, fn=''):
		return self.tkFileDialog.asksaveasfilename(title=title, initialfile=fn)
	def choose_dir(self, title=None):
		return self.tkFileDialog.askdirectory(title=title)

class BuiltinDManager:
	def __init__(self):
		self.urllib2=__import__('urllib2')
	def down(self, url, fn):
		u = self.urllib2.urlopen(url)
		f = open(fn, 'wb')
		f.write(u.read())
		f.close()
		u.close()
	def down_file(self, url):
		fn = FPICKER.save_one('Скачать', fn=self.urllib2.posixpath.basename(url))
		self.down(url, fn)
	def down_dir(self, urls, statusCb=None):
		fn = FPICKER.choose_dir(title='Скачать')
		for i in xrange(len(urls)):
			if statusCb: statusCb(i)
			url = urls[i]
			self.down(url, fn+'/'+self.urllib2.posixpath.basename(url))

FPICKER = TkFilePicker()
DM = BuiltinDManager()

