import time
from tornado.gen import coroutine
from tornado.web import RequestHandler
from auth.kancolle import KanColleAuth
from auth.exceptions import OoiAuthError
from utils.convert import to_int, to_str
from config import kcs_domain, kcs_https_domain


class MainHandler(RequestHandler):
    def get(self):
        play_mode = to_int(self.get_secure_cookie('play_mode'), 1)
        self.render('login_form.html', error=False, message=None, play_mode=play_mode)

    @coroutine
    def post(self):
        login_id = self.get_argument('login_id')
        password = self.get_argument('password')
        play_mode = to_int(self.get_argument('play_mode'), 1)
        if login_id and password:
            auth = KanColleAuth(login_id, password)
            try:
                flash_url, world_ip, token, starttime, owner = yield auth.get_flash()
                self.set_secure_cookie('owner', owner, expires_days=None)
                self.set_secure_cookie('world_ip', world_ip, expires_days=None)
                self.set_secure_cookie('token', token, expires_days=None)
                self.set_secure_cookie('starttime', starttime, expires_days=None)
                self.set_secure_cookie('play_mode', str(play_mode), expires=time.time()+86400)
                if play_mode == 2:
                    self.redirect('/iframe')
                elif play_mode == 3:
                    self.redirect('/poi')
                else:
                    self.redirect('/kancolle')
            except OoiAuthError as e:
                self.render('login_form.html', error=True, play_mode=play_mode,
                            message=e.message)

        else:
            self.render('login_form.html', error=True, play_mode=play_mode,
                        message='请输入完整的登录ID和密码')


class NormalGameHandler(RequestHandler):
    def get(self):
        owner = to_str(self.get_secure_cookie('owner'))
        world_ip = to_str(self.get_secure_cookie('world_ip'))
        token = to_str(self.get_secure_cookie('token'))
        starttime = to_str(self.get_secure_cookie('starttime'))
        if owner and world_ip and token and starttime:
            scheme = self.request.headers.get('X-Scheme', 'http')
            host = kcs_domain if kcs_domain else self.request.headers.get('Host')
            if scheme == 'https' and kcs_https_domain:
                host = kcs_https_domain
            self.render('normal_game.html', scheme=scheme, host=host, token=token, starttime=starttime,
                        world_ip=world_ip)
        else:
            self.clear_all_cookies()
            self.redirect('/')


class iFrameGameHandler(RequestHandler):
    def get(self):
        owner = to_str(self.get_secure_cookie('owner'))
        world_ip = to_str(self.get_secure_cookie('world_ip'))
        token = to_str(self.get_secure_cookie('token'))
        starttime = to_str(self.get_secure_cookie('starttime'))
        if owner and world_ip and token and starttime:
            self.render('iframe_game.html')
        else:
            self.clear_all_cookies()
            self.redirect('/')


class iFrameFlashHandler(RequestHandler):
    def get(self):
        owner = to_str(self.get_secure_cookie('owner'))
        world_ip = to_str(self.get_secure_cookie('world_ip'))
        token = to_str(self.get_secure_cookie('token'))
        starttime = to_str(self.get_secure_cookie('starttime'))
        if owner and world_ip and token and starttime:
            scheme = self.request.headers.get('X-Scheme', 'http')
            host = kcs_domain if kcs_domain else self.request.headers.get('Host')
            if scheme == 'https' and kcs_https_domain:
                host = kcs_https_domain
            self.render('flash.html', scheme=scheme, host=host, token=token, starttime=starttime,
                        world_ip=world_ip)
        else:
            self.clear_all_cookies()
            self.send_error(403)


class PoiGameHandler(RequestHandler):
    def get(self):
        owner = to_str(self.get_secure_cookie('owner'))
        world_ip = to_str(self.get_secure_cookie('world_ip'))
        token = to_str(self.get_secure_cookie('token'))
        starttime = to_str(self.get_secure_cookie('starttime'))
        if owner and world_ip and token and starttime:
            scheme = self.request.headers.get('X-Scheme', 'http')
            host = kcs_domain if kcs_domain else self.request.headers.get('Host')
            if scheme == 'https' and kcs_https_domain:
                host = kcs_https_domain
            self.render('poi_game.html', scheme=scheme, host=host, token=token, starttime=starttime,
                        world_ip=world_ip)
        else:
            self.clear_all_cookies()
            self.redirect('/')


class ReloginHandler(RequestHandler):
    def get(self):
        self.clear_all_cookies()
        self.redirect('/')


class MaintainHandler(RequestHandler):
    def get(self):
        self.render('maintain.html')
