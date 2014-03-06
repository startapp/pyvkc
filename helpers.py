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
	def down_file(self, url):
		fn = FPICKER.save_one('Скачать', fn=self.urllib2.posixpath.basename(url))
		u = self.urllib2.urlopen(url)
		f = open(fn, 'wb')
		f.write(u.read())
		f.close()
		u.close()
		return 1
	def down_dir(self, urls, statusCb=None):
		fn = FPICKER.choose_dir(title='Скачать')
		for i in xrange(len(urls)):
			if statusCb: statusCb(i)
			print urls[i]
			print urls
			url = urls[i]
			u = self.urllib2.urlopen(url)
			f = open(fn+'/'+self.urllib2.posixpath.basename(url), 'wb')
			f.write(u.read())
			f.close()
			u.close()

FPICKER = TkFilePicker()
DM = BuiltinDManager()

