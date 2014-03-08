# coding: utf-8
import random
import time
import urllib
import re
from hashlib import md5
from functools import partial
from vkconfig import *
try:
    import json
except ImportError:
    import simplejson as json
from vkontakte import http
import urllib

API_URL = 'http://api.vk.com/api.php'
SECURE_API_URL = 'http://api.vkontakte.ru/method/'
DEFAULT_TIMEOUT = 1
REQUEST_ENCODING = 'utf8'


# See full list of VK API methods here:
# http://vk.com/developers.php?o=-1&p=%D0%A0%D0%B0%D1%81%D1%88%D0%B8%D1%80%D0%B5%D0%BD%D0%BD%D1%8B%D0%B5_%D0%BC%D0%B5%D1%82%D0%BE%D0%B4%D1%8B_API&s=0
# http://vk.com/developers.php?o=-1&p=%D0%9E%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D0%B5_%D0%BC%D0%B5%D1%82%D0%BE%D0%B4%D0%BE%D0%B2_API&s=0
COMPLEX_METHODS = ['secure', 'ads', 'messages', 'likes', 'friends',
    'groups', 'photos', 'wall', 'newsfeed', 'notifications', 'audio',
    'video', 'docs', 'places', 'storage', 'notes', 'pages',
    'activity', 'offers', 'questions', 'subscriptions',
    'users', 'status', 'polls', 'account', 'auth', 'stats']


class VKError(Exception):
    __slots__ = ["error"]
    def __init__(self, error_data):
        self.error = error_data
        Exception.__init__(self, str(self))

    @property
    def code(self):
        return self.error['error_code']

    @property
    def description(self):
        return self.error['error_msg']

    @property
    def params(self):
        return self.error['request_params']

    def __str__(self):
        return "Error(code = '%s', description = '%s', params = '%s')" % (self.code, self.description, self.params)

def _encode(s):
    if isinstance(s, (dict, list, tuple)):
        s = json.dumps(s, ensure_ascii=False, encoding=REQUEST_ENCODING)

    if isinstance(s, unicode):
        s = s.encode(REQUEST_ENCODING)

    return s # this can be number, etc.


def signature(api_secret, meth, params):
#    keys = sorted(params.keys())
#    param_str = "&".join(["%s=%s" % (str(key), _encode(params[key])) for key in keys])
    param_str = urllib.unquote(urllib.urlencode(params))
    if DEBUG: print 'SIG=md5('+('/method/' + meth+'?' + param_str + '|' + str(api_secret))+')'
    return md5('/method/' + meth+'?' + param_str + str(api_secret)).hexdigest()

# We have to support this:
#
#   >>> vk = API(key, secret)
#   >>> vk.get('getServerTime')  # "get" is a method of API class
#   >>> vk.friends.get(uid=123)  # "get" is a part of vkontakte method name
#
# It works this way: API class has 'get' method but _API class doesn't.

class _API(object):
    def __init__(self, api_id=None, api_secret=None, token=None, **defaults):
        if not USE_API_RELAY:
            if not (api_id and api_secret or token):
                raise ValueError("Arguments api_id and api_secret or token are required")

        def captcha_callback(self, imgurl):
            print imgurl
            return raw_input()

        self.api_id = api_id
        self.api_secret = api_secret
        self.token = token
        self.defaults = defaults
        self.method_prefix = ''

    def _get(self, method, timeout=DEFAULT_TIMEOUT, sig = None, **kwargs):
        raw = kwargs['raw']
        print '95raw: ',raw
        if USE_API_RELAY == 0:
            print 'req'
            status, response = self._request(method, timeout=timeout, sig=sig, **kwargs)
            print 'answ'
            if not (200 <= status <= 299):
                raise VKError({
                    'error_code': status,
                    'error_msg': "HTTP error",
                    'request_params': kwargs,
                })
        else: #This is SWEET BREAD, not the code...
            relay = RELAY_SOCK_FILE;
            relay.write('REQE\n%s\n'%method);
            relay.flush()
            print 'req'
            if relay.readline().strip()=='OK':
                for key, value in kwargs.iteritems():
                    relay.write('PARA\n')
                    relay.write(key+'\n%d\n'%len(str(value)))
                    relay.write(str(value))
                relay.write('ENDP\n')
                relay.flush()
                print 'params'
                if relay.readline().strip() == 'ANSW':
                    print 'answ'
                    leng = int(relay.readline().strip())
                    print 'len=',leng
                    response = relay.read(leng)
                    print 'read'
                else: raise VKError('RELAY ERR.')
        data = json.loads(response, strict=False)
        print 'meth=', method
        print 'params=', kwargs
        print 'raw=',raw
        print 'response:'
        print data
        if isinstance(data, int): return data
        if "error" in data:
        #some vodka for my abstinent code...
            if int(data['error']['error_code']) == 5:
                import re
                s=re.findall('\'.+\'', data['error']['error_msg'])[0][1:-1]
                sig=md5(s+self.api_secret).hexdigest()
                return self._get(method, timeout=DEFAULT_TIMEOUT, sig = sig, **kwargs)
            else:
                if raw: return data
                raise VKError(data["error"])
        if raw: return data
        return data['response']
        

    def __getattr__(self, name):
        '''
        Support for api.<method>.<methodName> syntax
        '''
        if name in COMPLEX_METHODS:
            api = _API(api_id=self.api_id, api_secret=self.api_secret, token=self.token, **self.defaults)
            api.method_prefix = name + '.'
            return api

        # the magic to convert instance attributes into method names
        return partial(self, method=name)

    def __call__(self, sig=None, **kwargs):
        raw = 0
        try: raw = kwargs['raw']
        except: kwargs['raw']=0
        print '153raw: ', raw
        method = kwargs.pop('method')
        params = self.defaults.copy()
        params.update(kwargs)
        try:
            return self._get(self.method_prefix + method, sig=sig, **params)
        except VKError, e:
            if int(e.code==14):
                csid = e.error['captcha_sid']
                ckey = self.captcha_callback(e.error['captcha_img'])
                kwargs.update({
                    'captcha_sid': csid,
                    'captcha_key': ckey
                })
                return self.__call__(sig, **kwargs)
            if int(e.code==6):
                time.sleep(1)
                return self.__call__(sig, **kwargs)
            raise

    def _signature(self, meth, params):
        return signature(self.api_secret, meth, params)

    def _request(self, method, timeout=DEFAULT_TIMEOUT, sig=None, **kwargs):
        print 'req_'
        for key, value in kwargs.iteritems():
            print key, value
            kwargs[key] = _encode(value)

        if self.token:
            # http://vkontakte.ru/developers.php?oid=-1&p=Выполнение_запросов_к_API
            params = dict(
                access_token=self.token,
            )
            params.update(kwargs)
            params['timestamp'] = int(time.time())
            if self.api_secret: 
                if sig==None: params['sig'] = self._signature(method, params)
                else: params['sig'] = sig
            url = SECURE_API_URL + method
            secure = False
        else:
            # http://vkontakte.ru/developers.php?oid=-1&p=Взаимодействие_приложения_с_API
            params = dict(
                api_id=str(self.api_id),
                method=method,
                format='JSON',
                v='3.0',
                random=random.randint(0, 2 ** 30),
            )
            params.update(kwargs)
            params['timestamp'] = int(time.time())
            params['sig'] = self._signature(method, data)
            url = API_URL
            secure = False

        data = urllib.urlencode(params)
        headers = {"Accept": "application/json",
                   "Content-Type": "application/x-www-form-urlencoded"}

        # urllib2 doesn't support timeouts for python 2.5 so
        # custom function is used for making http requests
        return http.post(url, data, headers, timeout, secure=secure)


class API(_API):

    def get(self, method, timeout=DEFAULT_TIMEOUT, **kwargs):
        return self._get(method, timeout, **kwargs)
