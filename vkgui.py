#!/usr/bin/env python2
# -*- coding: utf-8 -*-

MY_APPNAME = 'PyVKC'
USE_GUI=1

import os
def configure():
	def apply():
		login = cwnd.login.get()
		passw = cwnd.passw.get()
		pnm = cwnd.pnm.get()
		extf = cwnd.extf.get()
		openm = cwnd.openvar.get()
		notifycmd = cwnd.notifycmd.get()
		probeinterval = '30' #TODO: NO HARDCODE!!!
		CSD=os.path.split(os.path.realpath(sys.argv[0]))[0]
		config_filename = os.path.join(CSD, 'vkconfig.txt')
		f = open(config_filename, 'w')
		f.write('#Не меняйте строки местами!\n%s #login\n%s #password\n%d #image to pnm\n%d #extra functions\n%s #open method\n%s #notify cmd\n%s #message probing interval\n'%(login, passw, pnm, extf, opem, notifycmd, probeinterval))
		f.close()
		cwnd.destroy()
	cwnd = Tk()
	cwnd.resizable(False, False)
	cwnd.title('Настройка %s'%MY_APPNAME)
	cwnd._login = Label(cwnd, text='E-mail/Phone: ')
	cwnd._login.grid(row=1, column=1, sticky='w')
	cwnd.login = Entry(cwnd)
	cwnd.login.grid(row=1, column=2, sticky='we')
	cwnd._passw = Label(cwnd, text='Пароль: ')
	cwnd._passw.grid(row=2, column=1, sticky='w')
	cwnd.passw = Entry(cwnd)
	cwnd.passw.grid(row=2, column=2, sticky='we')
	cwnd.pnm = IntVar()
	cwnd.pnm.set(0)
	cwnd._pnm = Checkbutton(cwnd, text='Показывать картинки через PNM.', variable=cwnd.pnm)
	cwnd.extf = IntVar()
	cwnd.extf.set(0)
	cwnd._extf = Checkbutton(cwnd, text='Включить дополнительные функции', variable=cwnd.extf)
	cwnd._pnm.grid(row=3, column=1, columnspan=2, sticky='w')
	cwnd._extf.grid(row=4, column=1, columnspan=2, sticky='w')
	cwnd.openmethods = {
		'Открывать файлы через xdg-open (UNIX)': 'xdg',
		'Открывать файлы через os.startfile (WINDOWS)': 'ossf',
	}
	cwnd.openvar = Listbox(cwnd, height=3)
	map(lambda x: cwnd.openvar.insert(END, x), cwnd.openmethods.keys())
	cwnd.openvar = StringVar()
	cwnd.openvar.set('xdg')
	row = 4
	for l,v in cwnd.openmethods.iteritems():
		rb = Radiobutton(cwnd, text=l, variable=cwnd.openvar, value=v)
		row+=1
		rb.grid(row=row, column=1, columnspan=2, sticky='w')
	row+=1
	cwnd._notifycmd = Label(cwnd, text='Команда нотификации о сообщени (vkgui nogui msgnotify): ')
	cwnd._notifycmd.grid(row=row, column=1, sticky='w')
	cwnd.notifycmd = Entry(cwnd)
	cwnd.notifycmd.grid(row=row, column=2, sticky='we')
	cwnd.ok = Button(cwnd, text='Сохранить', command=apply)
	row += 1
	cwnd.ok.grid(row=row, column=1, columnspan=2)
	cwnd.mainloop()

try:
	from vkconfig import *
except:
	from Tkinter import *
	configure()
	from vkconfig import *

import vkontakte
if not USE_API_RELAY:
	import vk_auth
else:
	import socket
import urllib2
from StringIO import StringIO
import time
import sys
import os
import helpers
import re
from Tkinter import *

LAST_SCOPETS = "friends,photos,messages,wall"

def _emojidel(txt):
	try:
	    # UCS-4
	    highpoints = re.compile(u'[\U00010000-\U0010ffff]')
	except re.error:
	    # UCS-2
	    highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
	return highpoints.sub(u'\u25FD', txt)

def _dtpn(udict):
	return udict['first_name'] + ' ' + udict['last_name']

def _get(url):
	u = urllib2.urlopen(url)
	return u

def load_image(url):
	global ROOT_WND
	from PIL import Image
	photo_stream = _get(url)
	photo_file = StringIO(photo_stream.read())
	photo_img = Image.open(photo_file)
	if not USE_PNM:
		from PIL import ImageTk
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
	except: return FDICT[name]
def _itn(agent, uid):
	u = agent.users.get(uids=uid)[0]
	return _dtpn(u)

def _get_user_albums(agent, name):
	ssw = [{u'aid':u'profile', u'title': u'Фотографии со страницы'},
			{u'aid': u'wall', u'title': u'Фотографии со стены'},
			{u'aid': u'saved', u'title': u'Сохраненные фотографии'},
]
	ssw += agent.photos.getAlbums(uid=_nti(name))
	return ssw

def _get_album_photos(agent, aid, uid=None, **kwargs):
	ssw = agent.photos.get(aid=aid, uid=uid, **kwargs)
	return ssw

def auth():
	scope = LAST_SCOPETS
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
		token, uid, secret = rld.split(' ')
		agent = vkontakte.API()	
	return token, uid, secret, agent

class StatusWindow:
	def __init__(self, parent=None, title='status'):
		if USE_GUI:
			self.st_wnd = Toplevel(parent)
			self.st_wnd.resizable(False, False)
			self.st_wnd.title(title)
			self.st_lbl = Label(self.st_wnd)
			self.st_lbl.pack()
	def set(self, string):
		if USE_GUI:
			self.st_lbl.config(text=string)
			self.st_wnd.update()
		string
	def destroy(self):
		if USE_GUI:
			self.st_wnd.destroy()

class BigJoint:
	def __init__(self, Z='main', *args):
		global USE_GUI
		self.cmd = Z
		self.args = args
		if self.cmd == "nogui":
			self.cmd = args[0]
			args = args[1:]
			USE_GUI=0
		if 1:
			#self.wnd = Tk()
#			self.wnd.resizable(False, False)
			#self.wnd.title(MY_APPNAME)
			#self.curr = Label(self.wnd, text=u'Вхожу в vk.com')
			#self.curr.pack()
			#self.wnd.after(100, self.start)
			#self.wnd.mainloop()
		#else:
			#self.wnd = None
			self.start()
	def start(self):
#		Все равно толку нет.
#		try:
			self.token, self.uid, self.secret, self.agent = auth()
			self.agent.captcha_callback = self.show_captcha
			#if USE_GUI: self.curr.config(text=u'Вход успешен. uid=%s'%self.uid)
			self.friends_init()
#		except:
			#return

	def show_captcha(self, img):
		def ok():
			self.captcha_key = txt_entr.get().strip()
			captcha_wnd.destroy()
		if USE_GUI:
			captcha_wnd = Toplevel()
			captcha_wnd.resizable(False, False)
			image = load_image(img)
			cp_label = Label(captcha_wnd, text=u'Введите текст с картинки:')
			cp_label.pack(side=LEFT)
			img_label = Label(captcha_wnd, image=image)
			img_label.image = image
			img_label.pack(side=BOTTOM)
			txt_entr = Entry(captcha_wnd)
			txt_entr.pack(side=BOTTOM, expand=1)
			ok_btn = Button(captcha_wnd, text='Ок', command=lambda: ok())
			self.wnd.wait_window(captcha_wnd)
			return self.captcha_key
		else:
			print 'CAPTCHA -', img, '>'
			return raw_input
	def like_set(self, **kwargs):
		il = int(self.agent.likes.isLiked(**kwargs))
		if il==0:
			self.agent.likes.add(**kwargs)
			print 'LIKE: '+repr(kwargs)
	def like_set_all(self, type, owner_id, items):
		for i in items:
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
		global USE_GUI, ROOT_WND
		global FDICT
		FDICT = {u'Я': int(self.uid)}
		#self.wnd.withdraw()
		self.wnd = Tk()
		ROOT_WND=self.wnd
#		self.wnd.resizable(False, False)
		self.wnd.title(MY_APPNAME)
		if self.cmd=='photoupload':
			if USE_GUI:
				self.wnd.withdraw()
			filename = self.args[0]
			return self.cmd_photoupload(u'Я', fname=filename)
		if self.cmd=='sendmsg':
			if USE_GUI:
				self.wnd.withdraw()
			uid = self.args[0]
			txt = sys.stdin.read()
			self.cmd_sendmsg(_uid=uid, txt=txt, rec=1)
			if USE_GUI: self.wnd.destroy()
		if self.cmd=='getmsg':
			if USE_GUI:
				USE_GUI=0
				self.wnd.destroy()
			print self.cmd_get_msg(mode=self.args[0])
		if self.cmd=='msgnotify':
			if USE_GUI:
				USE_GUI=0
				self.wnd.destroy()
			self.cmd_msg_notify()
		if not USE_GUI: return
		self.friends_frame = Frame(self.wnd)
		self.friends_scrollbar = Scrollbar(self.friends_frame, orient=VERTICAL)
		self.friends_listbox = Listbox(self.friends_frame, yscrollcommand=self.friends_scrollbar.set)
		self.friends_scrollbar.config(command=self.friends_listbox.yview)
		self.friends_scrollbar.pack(side=RIGHT, fill=Y)
		self.friends_listbox.pack(side=LEFT, fill=BOTH, expand=1)
		self.friends = self.agent.friends.get(fields="uid,first_name,last_name", order="hints")
		self.friends_listbox.insert(END, u'Я')
		for f in self.friends:
			fn = f['first_name']+' '+f['last_name']
			FDICT[fn] = f['uid']
			self.friends_listbox.insert(END, fn)
		#self.curr.destroy()
		self.friends_frame.pack(fill=X)
		self.buttons_frame = Frame(self.wnd)
		if self.cmd=='main':
			self.info_btn = Button(self.buttons_frame, text=u'Инфо', command=lambda: self.cmd_info(self.friends_listbox.get(ACTIVE)))
			self.info_btn.grid(row=1, column=1, columnspan=2, sticky='nesw')
			self.msg_btn = Button(self.buttons_frame, text=u'Отправить сбщ.', command=lambda: self.cmd_sendmsg(self.friends_listbox.get(ACTIVE)))
			self.msg_btn.grid(row=2, column=1, sticky='nesw')
			self.hist_btn = Button(self.buttons_frame, text=u'История', command=lambda: self.cmd_showhist(self.friends_listbox.get(ACTIVE)))
			self.hist_btn.grid(row=2, column=2, sticky='nesw')
			if SHOW_IMAGES:
				self.photo_btn = Button(self.buttons_frame, text=u'Фотки', command=lambda: self.cmd_albums(self.friends_listbox.get(ACTIVE)))
				self.photo_btn.grid(row=3, column=1, columnspan=2, sticky='nesw')
			if EXTRA_FUNC:
				self.sendall_btn = Button(self.buttons_frame, text=u'Рассылка сообщений', command=lambda: self.cmd_sendmsgtoall())
				self.sendall_btn.grid(row=4, column=1, sticky='nesw')
				self.histall_btn = Button(self.buttons_frame, text=u'Сохранить все переписки', command=lambda: self.cmd_showhist(self.friends_listbox.get(ACTIVE), all=1))
				self.histall_btn.grid(row=4, column=2, sticky='nesw')
				self.bdmap_btn = Button(self.buttons_frame, text=u'Сохранить дни рождения', command=lambda: self.cmd_bdmap())
				self.bdmap_btn.grid(row=5, column=1, columnspan=2, sticky='nesw')
			self.buttons_frame.pack()
			self.wnd.mainloop()

	def download_album(self, uid, album):
			photos = _get_album_photos(self.agent, album['aid'], uid)
			count = len(photos)
			st = StatusWindow(self.wnd, 'Сохраненяю фото...')
			st.set('Создаю список ссылок... Всего %d файлов.'%count)
			urls = []
			for i in xrange(len(photos)):
			  SAVE_SIZE='src_big'
			  print photos[i]
			  for j in xrange(1, len(SAVE_SIZES)+1):
			    if SAVE_SIZES[j] in photos[i].keys(): SAVE_SIZE=SAVE_SIZES[j]
			  print 'SIZE is', SAVE_SIZE
			  print photos[i][SAVE_SIZE]
			  urls+=[photos[i][SAVE_SIZE]]
			  st.set('Создаю список ссылок... %d/%d.'%(i, count))
			st.set('Начинаю закачку.')
			helpers.DM.down_dir(urls, statusCb=lambda x: st.set('Загружаю %d/%d...'%(x+1, count)))
			st.destroy()


	def cmd_albums(self, _uid, mode='std', callback=None):
		def like_all(album):
			photos = _get_album_photos(self.agent, album['aid'], uid)
			for p in photos:
				self.like_set(type='photo', owner_id=uid, item_id=p['pid'])

		uid = _nti(_uid)
		alb_wnd = Toplevel(self.wnd)
#		alb_wnd.resizable(False, False)
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
		buttons_frame.pack(side=BOTTOM)
		if mode=='std':
			view_btn = Button(buttons_frame, text=u'Смотреть', command=lambda: self.cmd_photos(dalbums[alb_listbox.get(ACTIVE)], uid))
			view_btn.grid(row=1, column=1)
			dwnall_btn = Button(buttons_frame, text=u'Скачать', command=lambda: self.download_album(uid, dalbums[alb_listbox.get(ACTIVE)]))
			dwnall_btn.grid(row=1, column=2)
			upl_btn = Button(buttons_frame, text=u'Выставить', command=lambda: self.cmd_photoupload(uid, album=dalbums[alb_listbox.get(ACTIVE)]))
			if uid==_nti(u'Я') and helpers.CAN_UPLOAD: upl_btn.grid(row=2, column=1, columnspan=2, sticky='nesw')
			if EXTRA_FUNC:
				lkall_btn = Button(buttons_frame, text=u'Лайкнуть все фотки', command=lambda: like_all(dalbums[alb_listbox.get(ACTIVE)]))
				lkall_btn.grid(row=3, column=1, columnspan=2, sticky='nesw')
		elif mode=='callback':
			view_btn = Button(buttons_frame, text=u'Ок', command=lambda: callback(dalbums[alb_listbox.get(ACTIVE)]))
			view_btn.grid(row=1, column=1)

	def cmd_comments(self, type='photo', title='Коменты', **kwargs):
		comments = []
		if type=='photo':
			comments = self.agent.photos.getComments(pid=kwargs['photo']['pid'], owner_id=kwargs['photo']['owner_id'])[1:]
		for c in comments:
			print _itn(self.agent, c[u'from_id']), ':', c[u'message']

	def cmd_photos(self, album, uid=None):
		cpage=1
		def photo_popup(event, photo):
			def cmdwrap(mtd, *args, **kwargs):
				popup.destroy()
				mtd(*args, **kwargs)
			popup = Toplevel(alb_wnd)
			popup.title('Фото')
			popup.resizable(False, False)
			print photo
			SAVE_SIZE='src_big'
			for i in xrange(1, len(SAVE_SIZES)+1):
			  print "probe="+SAVE_SIZES[i]
			  if SAVE_SIZES[i] in photo.keys(): SAVE_SIZE=SAVE_SIZES[i]
			print "DOWNLOAD SIZE is "+SAVE_SIZE
			dwn_btn=Button(popup, text='Скачать', command=lambda: cmdwrap(helpers.DM.down_file, photo[SAVE_SIZE]))
			open_btn=Button(popup, text='Открыть', command=lambda: cmdwrap(helpers.DM.open_user, photo[SAVE_SIZE]))
			open_btn.pack()
			like_btn = Button(popup, text='LIKE: %s'%str(self.agent.likes.isLiked(type='photo', item_id=photo['pid'], owner_id=photo['owner_id'])), command=lambda: cmdwrap(self.like_toggle, type='photo', item_id=photo['pid'], owner_id=photo['owner_id']))
			comm_btn = Button(popup, text='Комментари', command=lambda: cmdwrap(self.cmd_comments, type='photo', photo=photo))
			dwn_btn.pack()
			if EXTRA_FUNC: comm_btn.pack()
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
		photos = _get_album_photos(self.agent, aid, uid, rev=1)
		if len(photos)==0:
			no_lbl = Label(alb_frame, text=u'Нет фотографий')
			no_lbl.pack()
			return
		photos_grid = []
		for i in xrange(0, PHOTOLIST_ROWS):
			photos_grid += [[]]
			for j in xrange(0, PHOTOLIST_COLS):
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
		#info_wnd.resizable(False, False)
		info_wnd.title(u'%s - %s'%(_dtpn(user), MY_APPNAME))
		info_frame = Frame(info_wnd)
		info_frame.pack()
		maxw = INFO_MAX_WIDTH
		#Аватарка
		if SHOW_IMAGES:
			photo_lbl = Label(info_frame, text=u'Загружаю...')
			self.wnd.update()
			photo = load_image(user[PROFILE_PHOTO])
			photo_lbl.config(image=photo)
			photo_lbl.photo = photo
			maxw = photo.width()
			photo_lbl.pack(anchor=S)
		#Имя
		info_name = Label(info_frame, text=_dtpn(user))
		info_name.pack(anchor=W)
		#Статус
		info_status = Label(info_frame, text=user['status'], wraplength=maxw, justify=LEFT)
		info_status.pack(anchor=W)
		#User id
		info_uid = Label(info_frame, text='UID: %d'%user['uid'])
		info_uid.pack(anchor=W)
		#Дата рождения
		if 'bdate' in user.keys():
			info_25dimetoxy_4bromo_amphetamine = Label(info_frame, text=u'Дата рождения: '+user['bdate']) #DOB
			info_25dimetoxy_4bromo_amphetamine.pack(anchor=W)

	def cmd_photoupload(self, _uid, album=None, fname=None, attachments='', mode='std', callback=lambda: None):
		if not fname: fname=helpers.FPICKER.open_file(title='Загрузить фото...')
		if not album: return self.cmd_albums(_uid, mode='callback', callback=lambda x: self.cmd_photoupload(_uid, fname=fname, album=x))
		aid = album['aid']
		st_wnd = StatusWindow(self.wnd, title='Загрузка фото')
		st_wnd.set('Заливаю %s в %s'%(fname, album['title']))
		if aid=='wall': userver = self.agent.photos.getWallUploadServer()['upload_url']
		elif aid=='pm': userver = self.agent.photos.getMessagesUploadServer()['upload_url']
		else: userver = self.agent.photos.getUploadServer(aid=aid)['upload_url']
		response = helpers.upload(userver, 'photo', fname)
		res = helpers.json.loads(response, strict=False)
		st_wnd.set('Сохранение...\n%s'%res)
		if aid=='wall': res = self.agent.photos.saveWallPhoto(**res)[0]
		elif aid=='pm': res = self.agent.photos.saveMessagesPhoto(**res)[0]
		else: res = self.agent.photos.save(**res)[0]
		st_wnd.destroy()
		if mode=='callback': callback(res)
		else:
			if aid=='wall': self.agent.wall.post(attachments=res[u'id'])
			if self.cmd == 'photoupload': self.wnd.destroy()

	def cmd_sendmsg(self, _uid, photo=0, attach='', rec=0, txt='', uid=0, count=1):
		def cmd_ok(rec=rec, photo=photo, txt=txt):
			if not rec: txt = msg_tb.get(0.0, END)
			if not rec: photo = phVar.get()
			if not rec: count = int(cVar.get())
			if photo and not attach:
				self.cmd_photoupload(_uid=_uid, album={'aid':'pm', 'title':'Личка '+_uid}, mode='callback', callback=lambda x: self.cmd_sendmsg(_uid, photo=1, attach=x['id'], rec=1, txt=txt, uid=uid, count=count))
				msg_wnd.destroy()
			self.agent.messages.send(uid=uid, message=txt, attachment=attach)
			if not rec: msg_wnd.destroy()
		uid = _nti(_uid)
		if rec:
			return cmd_ok()
		msg_wnd = Toplevel(self.wnd)
		msg_wnd.resizable(False, False)
		msg_wnd.title(u'Отправить %s - %s'%(_uid, MY_APPNAME))
		msg_frame = Frame(msg_wnd)
		msg_frame.pack(side=TOP, fill=BOTH)
		msg_scrollbar = Scrollbar(msg_frame, orient=VERTICAL)
		msg_tb = Text(msg_frame, yscrollcommand=msg_scrollbar.set)
		msg_scrollbar.config(command=msg_tb.yview)
		msg_scrollbar.pack(side=RIGHT, fill=Y)
		msg_tb.pack(side=LEFT, fill=BOTH, expand=1)
		phVar = IntVar()
		phVar.set(photo)
		cVar = StringVar()
		cVar.set(str(count))
		buttons_frame = Frame(msg_wnd)
		ph_cb = Checkbutton(buttons_frame, text=u'Прикрепить фото', variable=phVar)
		ph_cb.grid(row=1, column=1, sticky='w', columnspan=2)
		c_en = Entry(buttons_frame, textvariable=cVar)
		c_en.grid(row=2, column=2, sticky='w')
		c_lbl = Label(buttons_frame, text=u'Кол-во повторов:')
		c_lbl.grid(row=2, column=1, sticky='e')
		snd_btn = Button(buttons_frame, text=u'Ок', command=lambda: cmd_ok())
		snd_btn.grid(row=3, column=1, columnspan=2, sticky='nesw')
		buttons_frame.pack(side=BOTTOM)

	def _getmsghist(self, uid, printname, status_cb=lambda:None, **kwargs):
		buf = u''
		msgs = self.agent.messages.getHistory(uid=uid, offset=0, **kwargs)
		count = msgs[0]
		curr=0
		buf += u'Переписка с %s, uid=%d, всего %d сообщений.\n'%(printname, uid, count)
		loaded_cnt = 0
		while curr<count:
			msgs = self.agent.messages.getHistory(uid=uid, offset=curr, count=200, **kwargs)
			msgs = msgs[1:]
			currcount = len(msgs)
			loaded_cnt += currcount
			buf += u'OFFSET %d, %d сообщений:\n'%(curr, currcount)
			curr += 200
			status_cb(loaded_cnt, count)
			for m in msgs:
				stime = helpers.ftime(m['date'])
				if m['out']:
					buf+=u'%s Я: %s\n'%(stime, m['body'])	
				else:
					buf+=u'%s %s: %s\n'%(stime, printname, m['body'])
		return _emojidel(buf).replace('<br>', '\n'+(' '*8))

	def cmd_showhist(self, _uid, all=0):
		def save(history, fn=''):
			if fn=='':
				fn = helpers.FPICKER.save_one(title=u'Сохранить переписку', fn='dialog %s.txt'%_uid)
			f = open(fn, 'wb')
			f.write(history)
			f.close()
		def save_all():
			savedir=helpers.FPICKER.choose_dir(title='Сохранить переписки')
			hist_sw=StatusWindow(self.wnd, title='Сохранение переписок')
			count = len(FDICT.keys())
			curr = 0
			for name, uid in FDICT.iteritems():
				try:
					curr += 1
					hist_sw.set('Сохраняю - %s (%d/%d)'%(name, curr, count))
					history = self._getmsghist(uid, name, rev=1, status_cb=lambda x, x2: hist_sw.set('Сохраняю - %s (%d/%d), %d/%d...'%(name, curr, count, x, x2)))
					save(fn=savedir+'/'+name+'.txt', history=history)
				except: continue
			hist_sw.destroy()
		uid = _nti(_uid)
		if all: return save_all()
		hist_sw=StatusWindow(self.wnd, title='Переписка с %s'%_uid)
		hist_sw.set('Загружаю сообщения...')
		history = self._getmsghist(uid, _uid, rev=1, status_cb=lambda x, x2: hist_sw.set('Загужено %s/%s сообщений...'%(x, x2)))
		hist_sw.destroy()
		msg_wnd = Toplevel(self.wnd)
		msg_wnd.resizable(False, False)
		msg_wnd.title(u'Переписка с %s - %s'%(_uid, MY_APPNAME))
		msgh_frame = Frame(msg_wnd)
		msgh_frame.pack(side=TOP, fill=BOTH)
		msgh_scrollbar = Scrollbar(msgh_frame, orient=VERTICAL)
		msgh_tb = Text(msgh_frame, yscrollcommand=msgh_scrollbar.set)
		msgh_scrollbar.config(command=msgh_tb.yview)
		msgh_scrollbar.pack(side=RIGHT, fill=Y)
		msgh_tb.pack(side=LEFT, fill=BOTH, expand=1)
		msgh_tb.insert(END, history)
		buttons_frame = Frame(msg_wnd)
		save_btn = Button(buttons_frame, text='Сохранить', command=lambda: save(history=msgh_tb.get(0.0, END)))
		save_btn.pack(side=LEFT)
		buttons_frame.pack(side=BOTTOM)

	def cmd_sendmsgtoall(self):
		def cmd_ok():
			if USE_GUI: msg_wnd.destroy()
			status = StatusWindow(self.wnd, 'Рассылка')
			status.set('Подготовка к отправке...')
			modeGS = gsVar.get()
			modeG = gVar.get()
			modeB = bVar.get()
			drFlag = drVar.get()
			delay = 3
			txt = msg_tb.get(0.0, END)
			users = self.agent.users.get(user_ids=(','.join(map(str, FDICT.values()))), fields='sex,bdate,city,country,photo_50,photo_100,photo_200_orig,photo_200,photo_400_orig,photo_max,photo_max_orig,online,online_mobile,lists,domain,has_mobile,contacts,connections,site,education,universities,schools,can_post,can_see_all_posts,can_see_audio,can_write_private_message,status,last_seen,common_count,relation,relatives,counters')
			for user in users:
				status.set('Проверяю соответствие для %s, uid=%d'%(_dtpn(user), user['uid']))
				sndFlag = 0
				if modeGS:
					if modeG and user['sex']==1: sndFlag=1
					if modeB and user['sex']==2: sndFlag=1
				else:
					sndFlag=1
				if sndFlag and not drFlag:
					self.agent.messages.send(uid=user['uid'], message=txt)
					time.sleep(delay)
			status.destroy()
		msg_wnd = Toplevel(self.wnd)
		msg_wnd.resizable(False, False)
		msg_wnd.title(u'Рассылка - %s'%(MY_APPNAME))
		msg_frame = Frame(msg_wnd)
		msg_frame.pack(side=TOP, fill=BOTH)
		msg_scrollbar = Scrollbar(msg_frame, orient=VERTICAL)
		msg_tb = Text(msg_frame, yscrollcommand=msg_scrollbar.set)
		msg_scrollbar.config(command=msg_tb.yview)
		msg_scrollbar.pack(side=RIGHT, fill=Y)
		msg_tb.pack(side=LEFT, fill=BOTH, expand=1)
		buttons_frame = Frame(msg_wnd)
		snd_btn = Button(buttons_frame, text=u'Ок', command=lambda: cmd_ok())
		gsVar = IntVar()
		gsVar.set(1)
		gVar = IntVar()
		gVar.set(0)
		gCb = Checkbutton(buttons_frame, text=u'Отправлять девкам', variable=gVar)
		bVar = IntVar()
		bVar.set(0)
		bCb = Checkbutton(buttons_frame, text=u'Отправлять пацанам', variable=bVar)
		drVar = IntVar()
		drVar.set(1)
		drCb = Checkbutton(buttons_frame, text=u'Симулировать отправку', variable=drVar)
		gCb.grid(row=1, column=1, columnspan=2)
		bCb.grid(row=2, column=1, columnspan=2)
		drCb.grid(row=3, column=1, columnspan=2)
		snd_btn.grid(row=5, column=1, columnspan=2)
		buttons_frame.pack(side=BOTTOM)

	def cmd_bdmap(self):
		fname = helpers.FPICKER.save_one(title=u'Сохранить дни рождения', fn='bdates.txt')
		fwr = open(fname, 'w')
		users = self.agent.users.get(user_ids=(','.join(map(str, FDICT.values()))), fields='first_name,last_name,bdate,uid')
		for user in users:
			if 'bdate' in user:
				fwr.write("%s\tuid=%d, bdate=%s\n"%(_dtpn(user), user['uid'], user['bdate']))

	def cmd_get_msg(self, mode):
		if mode=='unread_count':
			return self.agent.messages.get(filters=1, out=0)[0]
		if mode=='last':
			msg = self.agent.messages.get(count=1, out=0)[1]
			return '%s - %s'%(_itn(self.agent, msg['uid']), msg['body'])

	def cmd_msg_notify(self):
		while 1:
			unread_cnt = self.cmd_get_msg('unread_count')
			if unread_cnt > 0: os.popen(MESSAGE_NOTIFY) #TODO: WAIT FOR EXIT
			time.sleep(MESSAGE_PROBE_INTERVAL)

if USE_API_RELAY:
	vkontakte.api.RELAY_SOCK = socket.socket()
	vkontakte.api.RELAY_SOCK.connect((RELAY_ADDR, RELAY_PORT))
	vkontakte.api.RELAY_SOCK_FILE = vkontakte.api.RELAY_SOCK.makefile()
	RELAY_SOCK_FILE = vkontakte.api.RELAY_SOCK_FILE

if __name__=='__main__':
	FDICT = {}
	args = sys.argv[1:]
	try:
		if args[0] == 'nogui':
			USE_GUI=0
			args = args[1:]
		else: from Tkinter import *
	except: from Tkinter import *
	bj = BigJoint(*args)
