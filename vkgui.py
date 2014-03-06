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
import os
import helpers

MY_APPNAME = 'PyVKC'

def download_user(url):
	return helpers.DM.down_file(url)

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

def open_user(url, ft='std'):
	fn = OPEN_TMPDIR+'/'+helpers.DM.urllib2.posixpath.basename(url)
	helpers.DM.down(url, fn)
	if OPEN_XDG:
		os.system('xdg-open "%s"'%fn)

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
	scope = "friends,photos,wall"
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

class StatusWindow:
	def __init__(self, parent, title):
		self.st_wnd = Toplevel(parent)
		self.st_wnd.resizable(False, False)
		self.st_lbl = Label(self.st_wnd)
		self.st_lbl.pack()
	def set(self, string):
		self.st_lbl.config(text=string)
		self.st_wnd.update()
	def destroy(self):
		self.st_wnd.destroy()

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

	def like_set(self, **kwargs):
		il = int(self.agent.likes.isLiked(**kwargs))
		if il==0:
			self.agent.likes.add(**kwargs)
	def like_set_all(self, type, owner_id, items):
		for i in items:
			print 'Like set to: '+type+str(i)
			like_set(type=type, owner_id=owner_id, item_id=i)

	def like_unset(self, **kwargs):
		il = int(self.agent.likes.isLiked(**kwargs))
		if il==1:
			self.agent.likes.delete(**kwargs)

	def like_toggle(self, **kwargs):
		il = int(self.agent.likes.isLiked(**kwargs))
		if il==0:
			self.agent.likes.add(**kwargs)
		elif il==1:
			self.agent.likes.delete(**kwargs)
		il = self.agent.likes.isLiked(**kwargs)

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
		def like_all(album):
			photos = _get_album_photos(self.agent, album['aid'], uid)
			for p in photos:
				self.like_set(type='photo', owner_id=uid, item_id=p['pid'])

		def download_all(album):
			photos = _get_album_photos(self.agent, album['aid'], uid)
			count = len(photos)
			st = StatusWindow(alb_wnd, 'Сохраненяю фото...')
			st.set('Создаю список ссылок... Всего %d файлов.'%count)
			urls = []
			for i in xrange(len(photos)):
				urls+=[photos[i][SAVE_SIZE]]
				print photos[i][SAVE_SIZE]
				st.set('Создаю список ссылок... %d/%d.'%(i, count))
			st.set('Начинаю закачку.')
			helpers.DM.down_dir(urls, statusCb=lambda x: st.set('Загружаю %d/%d...'%(x+1, count)))
			st.destroy()

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
		view_btn.grid(row=1, column=1)
		dwnall_btn = Button(buttons_frame, text=u'Скачать', command=lambda: download_all(dalbums[alb_listbox.get(ACTIVE)]))
		dwnall_btn.grid(row=1, column=2)
		if EXTRA_FUNC:
			lkall_btn = Button(buttons_frame, text=u'Проставить', command=lambda: like_all(dalbums[alb_listbox.get(ACTIVE)]))
			lkall_btn.grid(row=2, column=1, columnspan=2, sticky='nesw')
		buttons_frame.pack(side=BOTTOM)

	def cmd_photos(self, album, uid=None):
		cpage=1
		def photo_popup(event, photo):
			def cmdwrap(mtd, *args, **kwargs):
				popup.destroy()
				mtd(*args, **kwargs)
			popup = Toplevel(alb_wnd)
			popup.title('Фото')
			popup.resizable(False, False)
			dwn_btn=Button(popup, text='Скачать', command=lambda: cmdwrap(download_user, photo[SAVE_SIZE]))
			open_btn=Button(popup, text='Открыть', command=lambda: cmdwrap(open_user, photo[SAVE_SIZE]))
			open_btn.pack()
			like_btn = Button(popup, text='LIKE: %s'%str(self.agent.likes.isLiked(type='photo', item_id=photo['pid'], owner_id=photo['owner_id'])), command=lambda: cmdwrap(self.like_toggle, type='photo', item_id=photo['pid'], owner_id=photo['owner_id']))
			dwn_btn.pack()
			like_btn.pack()
			

		def next_page():
			global cpage
			if cpage<page_cnt:
				cpage += 1
				change_page(cpage)
		def prev_page():
			global cpage
			if cpage>1:
				cpage -= 1
				change_page(cpage)
		def change_page(page):
			global cpage
			cpage = page
			cp_lbl.config(text='Страница: %d из %d'%(cpage, page_cnt))
			page -= 1
			for i in xrange(0, PHOTOLIST_ROWS):
				for j in xrange(0, PHOTOLIST_COLS):
					try:
					#if 1:
						print i, j, ':', page, i*PHOTOLIST_COLS+j
						photos_grid[i][j].photo = load_image(pages[page][i*PHOTOLIST_COLS+j][PHOTOLIST_SIZE])
						photos_grid[i][j].photo_def = pages[page][i*PHOTOLIST_COLS+j]
						photos_grid[i][j].config(image = photos_grid[i][j].photo)
						photos_grid[i][j].bind('<Button-1>', lambda e: photo_popup(e, e.widget.photo_def))
					except:
					#else:
						try:
							if USE_PNM: photos_grid[i][j].photo.blank()
							else:
								photos_grid[i][j].photo = ImageTk.PhotoImage('RGBA', '1x1')
						except: pass
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
				print i, j
				photos_grid[i] += [Label(alb_frame)]
				photos_grid[i][j].grid(row=i, column=j)
		page_capacity = PHOTOLIST_ROWS*PHOTOLIST_COLS
		page_cnt = len(photos)/page_capacity+1
		pages = []
		for i in xrange(0, page_cnt):
			pages += [[]]
			for j in xrange(0, page_capacity):
				try:
					pages[i] += [photos[i*page_capacity+j]]
					print i, j, i*page_capacity+j
				except: break
		btn_frame = Frame(alb_wnd)
		pp_btn = Button(btn_frame, text='<-', command=prev_page)
		pp_btn.grid(row=0, column=0)
		np_btn = Button(btn_frame, text='->', command=next_page)
		np_btn.grid(row=0, column=2)
		cp_lbl = Label(btn_frame)
		cp_lbl.grid(row=0, column=1)
		btn_frame.pack()
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
