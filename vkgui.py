#!/usr/bin/env python
# -*- coding: utf-8 -*-

from vkconfig import *
from Tkinter import *
import vkontakte
if not USE_API_RELAY:
	import vk_auth
else:
	import socket
import urllib2
from PIL import Image, ImageTk
from StringIO import StringIO
import time
import sys
reload(sys)
sys.setdefaultencoding('utf8')

MY_APPNAME = 'PyVKC'

def _dtpn(udict):
	return udict['first_name'] + ' ' + udict['last_name']

def _get(url):
	u = urllib2.urlopen(url)
	return u

def load_image(url):
	photo_stream = _get(url)
	photo_file = StringIO(photo_stream.read())
	photo_img = Image.open(photo_file)
	if not USE_PNM:
		res = ImageTk.PhotoImage(photo_img)
	else:
		fname = PNM_TEMP+str(time.time())+'.ppm'
		photo_img.save(fname)
		res = PhotoImage(file = fname)
	photo_file.close()
	photo_stream.close()
	return res

def _nti(name):
	try: return int(name)
	except: pass
	return FDICT[name]

def _get_user_albums(agent, name):
	ssw = [{u'aid':u'profile', u'title': u'Фотографии со страницы'},
			{u'aid': u'wall', u'title': u'Фотографии со стены'},
			{u'aid': u'saved', u'title': u'Сохраненные фотографии'},
]
	ssw += agent.photos.getAlbums(uid=_nti(name))
	return ssw

def _get_album_photos(agent, aid, uid=None):
	ssw = agent.photos.get(aid=aid, uid=uid)
	return ssw

def auth():
	scope = "friends,photos"
	if not USE_API_RELAY:
		(token, uid, secret) = vk_auth.auth(LOGIN, PASS, APPID, scope+",nohttps")
		agent = vkontakte.API(token=token, api_secret=secret)
	else:
		rsf = RELAY_SOCK_FILE
		rsf.write('LOG1\n%s %s %s\n'%(LOGIN, PASS, APPID))
		rsf.flush()
		rsf.write(scope+'\n')
		rsf.flush()
		rld = rsf.readline().strip()
		print rld
		token, uid, secret = rld.split(' ')
		agent = vkontakte.API()	
	return token, uid, secret, agent

class BigJoint:
	def __init__(self):
		self.wnd = Tk()
		self.wnd.resizable(False, False)
		self.wnd.title(MY_APPNAME)
		self.curr = Label(self.wnd, text=u'Вхожу в vk.com')
		self.curr.pack()
		self.wnd.after(100, self.start)
		self.wnd.mainloop()
	def start(self):
#		Все равно толку нет.
#		try:
			self.token, self.uid, self.secret, self.agent = auth()
			self.curr.config(text=u'Вход успешен. uid=%s'%self.uid)
			self.friends_init()
#		except:
			#return

	def friends_init(self):
		global FDICT
		self.friends_frame = Frame(self.wnd)
		self.friends_scrollbar = Scrollbar(self.friends_frame, orient=VERTICAL)
		self.friends_listbox = Listbox(self.friends_frame, yscrollcommand=self.friends_scrollbar.set)
		self.friends_scrollbar.config(command=self.friends_listbox.yview)
		self.friends_scrollbar.pack(side=RIGHT, fill=Y)
		self.friends_listbox.pack(side=LEFT, fill=BOTH, expand=1)
		self.friends = self.agent.friends.get(fields="uid,first_name,last_name", order="hints")
		FDICT = {u'Я': self.uid}
		self.friends_listbox.insert(END, u'Я')
		for f in self.friends:
			fn = f['first_name']+' '+f['last_name']
			FDICT[fn] = f['uid']
			self.friends_listbox.insert(END, fn)
		self.curr.destroy()
		self.friends_frame.pack(fill=X)
		self.buttons_frame = Frame(self.wnd)
		self.info_btn = Button(self.buttons_frame, text=u'Инфо', command=lambda: self.cmd_info(self.friends_listbox.get(ACTIVE)))
		self.info_btn.pack(side=LEFT, fill=BOTH, expand=1)
		if SHOW_IMAGES:
			self.photo_btn = Button(self.buttons_frame, text=u'Фотки', command=lambda: self.cmd_albums(self.friends_listbox.get(ACTIVE)))
			self.photo_btn.pack(side=LEFT, fill=BOTH, expand=1)
		self.buttons_frame.pack()

	def cmd_albums(self, _uid):
		uid = _nti(_uid)
		alb_wnd = Toplevel(self.wnd)
		alb_wnd.resizable(False, False)
		alb_wnd.title(u'Альбомы %s - %s'%(_uid, MY_APPNAME))
		alb_frame = Frame(alb_wnd)
		alb_frame.pack(side=TOP, fill=BOTH)
		alb_scrollbar = Scrollbar(alb_frame, orient=VERTICAL)
		alb_listbox = Listbox(alb_frame, yscrollcommand=alb_scrollbar.set)
		alb_scrollbar.config(command=alb_listbox.yview)
		alb_scrollbar.pack(side=RIGHT, fill=Y)
		alb_listbox.pack(side=LEFT, fill=BOTH, expand=1)
		albums = _get_user_albums(self.agent, uid)
		dalbums = {}
		for a in albums:
			alb_listbox.insert(END, a['title'])
			dalbums[a['title']] = a
		buttons_frame = Frame(alb_wnd)
		view_btn = Button(buttons_frame, text=u'Смотреть', command=lambda: self.cmd_photos(dalbums[alb_listbox.get(ACTIVE)], uid))
		view_btn.pack(side=LEFT, fill=BOTH, expand=1)
		buttons_frame.pack(side=BOTTOM)

	def cmd_photos(self, album, uid=None):
		cpage=1
		pages=1
		def page_next():
			if cpage<=pages:
				cpage += 1
				change_page(cpage)
		def change_page(page):
			cpage = page
			page -= 1
			for i in xrange(0, PHOTOLIST_ROWS):
				for j in xrange(0, PHOTOLIST_COLS):
					try:
						photos_grid[i][j].photo = load_image(pages[page][i*PHOTOLIST_ROWS+j]['src_small'])
						photos_grid[i][j].config(image = photos_grid[i][j].photo)
					except:
						photos_grid[i][j].config(image = None, text='')
		aid = album['aid']
		alb_wnd = Toplevel(self.wnd)
		alb_wnd.resizable(False, False)
		alb_wnd.title('Альбом %s - %s'%(album['title'], MY_APPNAME))
		alb_frame = Frame(alb_wnd)
		alb_frame.pack(side=TOP, fill=BOTH)
		photos = _get_album_photos(self.agent, aid, uid)
		if len(photos)==0:
			no_lbl = Label(alb_frame, text=u'Нет фотографий')
			no_lbl.pack()
			return
		photos_grid = []
		for i in xrange(0, PHOTOLIST_ROWS):
			photos_grid += [[]]
			for j in xrange(0, PHOTOLIST_COLS):
				photos_grid[i] += [Label(alb_frame, text='img[%d][%d]'%(i,j))]
				photos_grid[i][j].grid(row=i, column=j)
		print 'PHCNT=%d'%len(photos)
		page_capacity = PHOTOLIST_ROWS*PHOTOLIST_COLS
		print 'PCAP=%d'%page_capacity
		page_cnt = len(photos)/page_capacity+1
		print 'PGCNT=%d'%page_cnt
		pages = []
		for i in xrange(0, page_cnt):
			pages += [[]]
			print 'Generating page: %d'%i
			for j in xrange(0, page_capacity):
				try:
					pages[i] += [photos[i*page_capacity+j]]
				except: break
		change_page(1)


	def cmd_info(self, uid=''):
		uid = _nti(uid)
		user = self.agent.users.get(user_ids=uid, fields='sex,bdate,city,country,photo_50,photo_100,photo_200_orig,photo_200,photo_400_orig,photo_max,photo_max_orig,online,online_mobile,lists,domain,has_mobile,contacts,connections,site,education,universities,schools,can_post,can_see_all_posts,can_see_audio,can_write_private_message,status,last_seen,common_count,relation,relatives,counters')[0]
		info_wnd = Toplevel(self.wnd)
		info_wnd.resizable(False, False)
		info_wnd.title(u'%s - %s'%(_dtpn(user), MY_APPNAME))
		info_frame = Frame(info_wnd)
		info_frame.pack()
		maxw = INFO_MAX_WIDTH
		#Аватарка
		if SHOW_IMAGES:
			photo_lbl = Label(info_frame, text=u'Загружаю...')
			photo_lbl.pack(anchor=S)
			self.wnd.update()
			photo = load_image(user[PROFILE_PHOTO])
			photo_lbl.config(image=photo)
			photo_lbl.photo = photo
			maxw = photo.width()
		#Имя
		info_name = Label(info_frame, text=_dtpn(user))
		info_name.pack(anchor=W)
		#Статус
		info_status = Label(info_frame, text=user['status'], wraplength=maxw, justify=LEFT)
		info_status.pack(anchor=W)
		#Дата рождения
		if 'bdate' in user.keys():
			info_25dimetoxy_4bromo_amphetamine = Label(info_frame, text=u'Дата рождения: '+user['bdate']) #DOB
			info_25dimetoxy_4bromo_amphetamine.pack(anchor=W)



if USE_API_RELAY:
	vkontakte.api.RELAY_SOCK = socket.socket()
	vkontakte.api.RELAY_SOCK.connect((RELAY_ADDR, RELAY_PORT))
	vkontakte.api.RELAY_SOCK_FILE = vkontakte.api.RELAY_SOCK.makefile()
	RELAY_SOCK_FILE = vkontakte.api.RELAY_SOCK_FILE
	print "Using relay server: "+RELAY_SOCK_FILE.readline()

FDICT = {}
bj = BigJoint()
