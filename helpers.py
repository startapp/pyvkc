#!/usr/bin/python
# -*- coding: utf-8 -*-

from vkconfig import *
import urllib2, urlparse
import os
import tkFileDialog
from vkontakte.api import json
import httplib, mimetypes
import codecs

def post_multipart(host, selector, fields, files):
    """
    Post fields and files to an http host as multipart/form-data.
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return the server's response page.
    """
    content_type, body = encode_multipart_formdata(fields, files)
    h = httplib.HTTP(host)
    h.putrequest('POST', selector)
    h.putheader('content-type', content_type)
    h.putheader('content-length', str(len(body)))
    h.endheaders()
    h.send(body)
    errcode, errmsg, headers = h.getreply()
    return h.file.read()

def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

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
	if OPEN_XDG:
		os.system('xdg-open "%s"'%fn)
	elif OPEN_WIN_OSSF:
		os.startfile(fn)

def upload(url, ff, fn):
	f=codecs.open(fn, 'rb', 'latin1')
	v=f.read()
	f.close()
	urlparts = urlparse.urlsplit(url)
	print post_multipart(urlparts[1], urlparts[2], {}, [[ff, fn, v]])

FPICKER = TkFilePicker()
DM = BuiltinDManager()

