import time
from collections import OrderedDict

from tornado.gen import coroutine
from tornado.web import RequestHandler

from auth.kancolle import KanColleAuth
from auth.exceptions import OoiAuthError
from session.session import OoiSession
from utils.convert import to_int, to_str
from config import cdn_domains

Session = OoiSession()
default_kcs_domain = None


def init_cdns(request):
    global cdn_domains
    if cdn_domains is None:
        cdn_domains = OrderedDict()
        cdn_domains['default'] = {'name': '不使用CDN加速 (较慢)', 'domain': request.headers.get('Host'), 'http': False}


class MainHandler(RequestHandler):
    def get(self):
        init_cdns(self.request)
        play_mode = to_int(self.get_secure_cookie('play_mode'), 1)
        default_cdn = list(cdn_domains.keys())[0] if cdn_domains else 'default'
        cdn = to_str(self.get_secure_cookie('cdn'), default_cdn)
        scheme = self.request.headers.get('X-Scheme', 'http')
        if scheme != 'https':
            self.redirect('https://%s%s' % (cdn_domains['default']['domain'], self.request.uri))
        else:
            self.render('login_form.html', error=False, message=None, play_mode=play_mode,
                        cdn=cdn, cdn_domains=cdn_domains)

    @coroutine
    def post(self):
        login_id = self.get_argument('login_id')
        password = self.get_argument('password')
        play_mode = to_int(self.get_argument('play_mode'), 1)
        cdn = self.get_argument('cdn')
        if cdn not in cdn_domains:
            cdn = 'default'
        if login_id and password:
            auth = KanColleAuth(login_id, password)
            try:
                flash_url, world_ip, token, starttime, owner = yield auth.get_flash()
                self.set_secure_cookie('owner', owner, expires_days=None)
                self.set_secure_cookie('token', token, expires_days=None)
                self.set_secure_cookie('starttime', starttime, expires_days=None)
                self.set_secure_cookie('play_mode', str(play_mode), expires=time.time()+86400)
                self.set_secure_cookie('cdn', cdn, expires_days=None)
                Session.create_user(owner, token, starttime, world_ip)
                if play_mode == 2:
                    self.redirect('/iframe')
                elif play_mode == 3:
                    self.redirect('/poi')
                else:
                    self.redirect('/kancolle')
            except OoiAuthError as e:
                self.render('login_form.html', error=True, play_mode=play_mode, cdn=cdn, cdn_domains=cdn_domains,
                            message=e.message)

        else:
            self.render('login_form.html', error=True, play_mode=play_mode, cdn=cdn, cdn_domains=cdn_domains,
                        message='请输入完整的登录ID和密码')


class NormalGameHandler(RequestHandler):
    def get(self):
        init_cdns(self.request)
        owner = to_str(self.get_secure_cookie('owner'))
        token = to_str(self.get_secure_cookie('token'))
        starttime = to_str(self.get_secure_cookie('starttime'))
        cdn = to_str(self.get_secure_cookie('cdn'))
        scheme = self.request.headers.get('X-Scheme', 'http')
        if owner and token and starttime and cdn:
            if cdn_domains[cdn]['http'] and scheme != 'http':
                self.redirect('http://%s/kancolle' % self.request.headers.get('Host'))
            else:
                pass
            user = Session.get_user(owner, token, starttime)
            if user:
                host = cdn_domains[cdn]['domain']
                self.render('normal_game.html', scheme=scheme, host=host, token=token, starttime=starttime, owner=owner)
                return
        self.clear_all_cookies()
        self.redirect('/')


class IFrameGameHandler(RequestHandler):
    def get(self):
        if self.request.headers.get('X-Scheme') == 'https':
            self.redirect('http://%s/iframe' % self.request.headers.get('Host'))
        owner = to_str(self.get_secure_cookie('owner'))
        token = to_str(self.get_secure_cookie('token'))
        starttime = to_str(self.get_secure_cookie('starttime'))
        cdn = to_str(self.get_secure_cookie('cdn'))
        if owner and token and starttime and cdn:
            user = Session.get_user(owner, token, starttime)
            if user:
                self.render('iframe_game.html')
                return
        self.clear_all_cookies()
        self.redirect('/')


class IFrameFlashHandler(RequestHandler):
    def get(self):
        owner = to_str(self.get_secure_cookie('owner'))
        token = to_str(self.get_secure_cookie('token'))
        starttime = to_str(self.get_secure_cookie('starttime'))
        cdn = to_str(self.get_secure_cookie('cdn'))
        if owner and token and starttime and cdn:
            user = Session.get_user(owner, token, starttime)
            if user:
                scheme = self.request.headers.get('X-Scheme', 'http')
                if cdn == 'default' or scheme == 'https':
                    host = default_kcs_domain if default_kcs_domain else self.request.headers.get('Host')
                else:
                    host = cdn_domains[cdn]['domain']
                self.render('flash.html', scheme=scheme, host=host, token=token, starttime=starttime, owner=owner)
                return
        self.clear_all_cookies()
        self.send_error(403)


class PoiGameHandler(RequestHandler):
    def get(self):
        if self.request.headers.get('X-Scheme') == 'https':
            self.redirect('http://%s/poi' % self.request.headers.get('Host'))
        owner = to_str(self.get_secure_cookie('owner'))
        token = to_str(self.get_secure_cookie('token'))
        starttime = to_str(self.get_secure_cookie('starttime'))
        cdn = to_str(self.get_secure_cookie('cdn'))
        if owner and token and starttime and cdn:
            user = Session.get_user(owner, token, starttime)
            if user:
                scheme = self.request.headers.get('X-Scheme', 'http')
                if cdn == 'default' or scheme == 'https':
                    host = default_kcs_domain if default_kcs_domain else self.request.headers.get('Host')
                else:
                    host = cdn_domains[cdn]['domain']
                self.render('poi_game.html', scheme=scheme, host=host, token=token, starttime=starttime, owner=owner)
                return
        self.clear_all_cookies()
        self.redirect('/')


class ReloginHandler(RequestHandler):
    def get(self):
        self.clear_all_cookies()
        self.redirect('https://%s/' % self.request.headers.get('Host'))


class MaintainHandler(RequestHandler):
    def get(self):
        self.render('maintain.html')
